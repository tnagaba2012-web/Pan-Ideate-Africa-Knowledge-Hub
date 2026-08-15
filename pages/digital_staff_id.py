"""
PAN IDEATE AFRICA — SECURE DIGITAL STAFF ID & ACCESS VERIFICATION

Features
- Automatic permanent PIA staff ID generation
- Secure random verification token (never exposes sensitive data in QR/barcode)
- QR code + Code 128 barcode generation
- Digital ID card preview
- PDF ID card download
- Super Admin ID issuance / regeneration / revocation
- USB barcode/QR scanner friendly verification screen
- Verification events recorded in the existing audit log when available

Designed to live at: pages/digital_staff_id.py
"""

import io
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

try:
    import qrcode
except ImportError:
    qrcode = None
import streamlit as st
from PIL import Image
from reportlab.graphics import renderPM
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from utils.database import get_connection

try:
    from pages.audit_log import log_audit_event
except Exception:
    log_audit_event = None


ID_PREFIX = "PIA-STAFF-"
DEFAULT_VALIDITY_YEARS = 3


def _column_names(connection):
    return {
        row[1]
        for row in connection.execute("PRAGMA table_info(staff_users)").fetchall()
    }


def ensure_staff_id_fields():
    """Safely add the Digital ID fields to the existing staff_users table."""
    connection = get_connection()
    try:
        columns = _column_names(connection)
        fields = {
            "digital_staff_id": "TEXT",
            "digital_id_token": "TEXT",
            "digital_id_issued_at": "TEXT",
            "digital_id_expires_at": "TEXT",
            "digital_id_status": "TEXT DEFAULT 'Active'",
            "digital_id_version": "INTEGER DEFAULT 1",
        }
        for name, definition in fields.items():
            if name not in columns:
                connection.execute(
                    f"ALTER TABLE staff_users ADD COLUMN {name} {definition}"
                )
        connection.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_staff_digital_id "
            "ON staff_users(digital_staff_id)"
        )
        connection.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_staff_digital_token "
            "ON staff_users(digital_id_token)"
        )
        connection.commit()
    finally:
        connection.close()


def _next_staff_number(connection):
    rows = connection.execute(
        "SELECT digital_staff_id FROM staff_users "
        "WHERE digital_staff_id LIKE ?",
        (f"{ID_PREFIX}%",),
    ).fetchall()
    numbers = []
    for row in rows:
        value = row[0] or ""
        try:
            numbers.append(int(value.replace(ID_PREFIX, "")))
        except (TypeError, ValueError):
            continue
    return max(numbers, default=0) + 1


def issue_digital_id(staff_id, validity_years=DEFAULT_VALIDITY_YEARS, force=False):
    """Issue or renew one staff member's secure Digital ID."""
    ensure_staff_id_fields()
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM staff_users WHERE id = ? LIMIT 1", (staff_id,)
        ).fetchone()
        if not row:
            return False, "Staff member not found."

        existing_id = row["digital_staff_id"] if "digital_staff_id" in row.keys() else None
        existing_token = row["digital_id_token"] if "digital_id_token" in row.keys() else None
        existing_status = row["digital_id_status"] if "digital_id_status" in row.keys() else None

        if existing_id and existing_token and existing_status == "Active" and not force:
            return True, existing_id

        number = _next_staff_number(connection) if not existing_id else int(existing_id.replace(ID_PREFIX, ""))
        digital_id = existing_id or f"{ID_PREFIX}{number:04d}"
        token = secrets.token_urlsafe(32)
        issued = datetime.utcnow()
        expires = issued + timedelta(days=365 * int(validity_years))
        version = int(row["digital_id_version"] or 0) + 1 if "digital_id_version" in row.keys() else 1

        connection.execute(
            """
            UPDATE staff_users
            SET digital_staff_id = ?,
                digital_id_token = ?,
                digital_id_issued_at = ?,
                digital_id_expires_at = ?,
                digital_id_status = 'Active',
                digital_id_version = ?
            WHERE id = ?
            """,
            (
                digital_id,
                token,
                issued.isoformat(timespec="seconds"),
                expires.isoformat(timespec="seconds"),
                version,
                staff_id,
            ),
        )
        connection.commit()

        if log_audit_event:
            try:
                log_audit_event(
                    actor_id=staff_id,
                    actor_name=row["full_name"],
                    actor_role=row["role"],
                    department=row["department"] if "department" in row.keys() else "",
                    module="Digital Staff ID",
                    action="ISSUE_ID" if not existing_id else "RENEW_ID",
                    target_type="staff_user",
                    target_id=str(staff_id),
                    summary=f"Digital Staff ID {digital_id} issued/renewed.",
                    details=f"ID version {version}; expires {expires.date().isoformat()}.",
                    severity="INFO",
                    outcome="SUCCESS",
                )
            except Exception:
                pass

        return True, digital_id
    finally:
        connection.close()


def ensure_all_staff_ids():
    """Give every existing staff member an ID without replacing existing IDs."""
    ensure_staff_id_fields()
    connection = get_connection()
    try:
        rows = connection.execute("SELECT id FROM staff_users ORDER BY id").fetchall()
    finally:
        connection.close()

    results = []
    for row in rows:
        results.append(issue_digital_id(row[0]))
    return results


def revoke_digital_id(staff_id):
    ensure_staff_id_fields()
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT digital_staff_id, full_name FROM staff_users WHERE id = ?",
            (staff_id,),
        ).fetchone()
        if not row:
            return False, "Staff member not found."
        connection.execute(
            "UPDATE staff_users SET digital_id_status = 'Revoked' WHERE id = ?",
            (staff_id,),
        )
        connection.commit()
        return True, f"Digital ID {row['digital_staff_id'] or 'not issued'} revoked."
    finally:
        connection.close()


def get_staff_id_record(staff_id):
    ensure_staff_id_fields()
    connection = get_connection()
    try:
        return connection.execute(
            "SELECT * FROM staff_users WHERE id = ? LIMIT 1", (staff_id,)
        ).fetchone()
    finally:
        connection.close()


def verify_staff_identity(scan_value):
    """Verify a scanner input using either Digital ID or secure token."""
    ensure_staff_id_fields()
    value = (scan_value or "").strip()
    if not value:
        return None, "Enter or scan a Staff ID / QR token."

    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT * FROM staff_users
            WHERE digital_staff_id = ? OR digital_id_token = ?
            LIMIT 1
            """,
            (value, value),
        ).fetchone()
    finally:
        connection.close()

    if not row:
        return None, "INVALID ID — no matching Digital Staff ID was found."

    status = row["digital_id_status"] or "Unknown"
    account_status = row["status"] or "Unknown"
    expires_raw = row["digital_id_expires_at"]

    if status != "Active":
        return row, f"ACCESS DENIED — Digital ID status is {status}."
    if account_status != "Active":
        return row, f"ACCESS DENIED — staff account status is {account_status}."

    if expires_raw:
        try:
            expires = datetime.fromisoformat(expires_raw)
            if datetime.utcnow() > expires:
                return row, "ACCESS DENIED — Digital ID has expired."
        except ValueError:
            return row, "ACCESS DENIED — Digital ID expiry record is invalid."

    return row, "ACCESS GRANTED — Digital Staff ID verified."


def _qr_bytes(token):
    if qrcode is None:
        raise RuntimeError("The QR-code package is not installed. Add qrcode[pil] to requirements.txt and reinstall dependencies.")
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output.getvalue()


def _barcode_bytes(value):
    drawing = createBarcodeDrawing(
        "Code128",
        value=value,
        barHeight=42,
        barWidth=1.2,
        humanReadable=True,
    )
    return renderPM.drawToString(drawing, fmt="PNG")


def _safe(value):
    return str(value or "—")


def build_id_pdf(row):
    """Generate a wallet-sized landscape PDF staff ID card."""
    width, height = (340, 215)
    output = io.BytesIO()
    pdf = canvas.Canvas(output, pagesize=(width, height))

    # Card background/border
    pdf.roundRect(8, 8, width - 16, height - 16, 12, stroke=1, fill=0)
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(22, height - 30, "PAN IDEATE AFRICA")
    pdf.setFont("Helvetica", 7.5)
    pdf.drawString(22, height - 42, "SECURE DIGITAL STAFF IDENTIFICATION")

    # Photo placeholder — the existing directory does not currently store staff photos.
    pdf.roundRect(22, 83, 78, 88, 6, stroke=1, fill=0)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(61, 129, "PHOTO")
    pdf.setFont("Helvetica", 6.5)
    pdf.drawCentredString(61, 116, "Add staff photo")
    pdf.drawCentredString(61, 106, "in Staff Directory")

    x = 116
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(x, 158, _safe(row["full_name"]))
    pdf.setFont("Helvetica", 8.5)
    pdf.drawString(x, 144, _safe(row["job_title"] if "job_title" in row.keys() else row["role"]))
    pdf.drawString(x, 131, f"Department: {_safe(row['department']) if 'department' in row.keys() else '—'}")
    pdf.drawString(x, 118, f"Staff ID: {_safe(row['digital_staff_id'])}")
    pdf.drawString(x, 105, f"Status: {_safe(row['digital_id_status'])}")
    pdf.drawString(x, 92, f"Version: {_safe(row['digital_id_version'])}")

    qr = Image.open(io.BytesIO(_qr_bytes(row["digital_id_token"])))
    qr_path = io.BytesIO()
    qr.save(qr_path, format="PNG")
    qr_path.seek(0)
    pdf.drawImage(ImageReader(qr_path), width - 92, 22, width=62, height=62, preserveAspectRatio=True, mask="auto")

    barcode = Image.open(io.BytesIO(_barcode_bytes(row["digital_staff_id"])))
    barcode_path = io.BytesIO()
    barcode.save(barcode_path, format="PNG")
    barcode_path.seek(0)
    pdf.drawImage(ImageReader(barcode_path), 22, 30, width=185, height=43, preserveAspectRatio=True, mask="auto")

    pdf.setFont("Helvetica", 6.5)
    pdf.drawString(116, 76, "Scan to verify identity. Sensitive staff information is not stored in the code.")
    pdf.drawString(116, 64, f"Issued: {_safe(row['digital_id_issued_at'])[:10]}")
    pdf.drawString(116, 54, f"Expires: {_safe(row['digital_id_expires_at'])[:10]}")

    pdf.showPage()
    pdf.save()
    output.seek(0)
    return output.getvalue()


def _render_card(row):
    st.markdown(
        """
        <style>
        .pia-id-card {border:2px solid #1f5d7a;border-radius:20px;padding:22px;background:linear-gradient(135deg,#f8fcff,#eef6fb);box-shadow:0 8px 25px rgba(0,0,0,.10);}
        .pia-id-title {font-size:24px;font-weight:800;color:#174b67;}
        .pia-id-number {font-size:18px;font-weight:800;letter-spacing:1px;color:#174b67;}
        .pia-id-status {font-weight:800;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class='pia-id-card'>
          <div class='pia-id-title'>🪪 PAN IDEATE AFRICA</div>
          <div>Secure Digital Staff Identification</div>
          <hr>
          <div><strong>{_safe(row['full_name'])}</strong></div>
          <div>{_safe(row['job_title'] if 'job_title' in row.keys() else row['role'])}</div>
          <div>{_safe(row['department']) if 'department' in row.keys() else '—'}</div>
          <p class='pia-id-number'>{_safe(row['digital_staff_id'])}</p>
          <div class='pia-id-status'>Status: {_safe(row['digital_id_status'])}</div>
          <div>Valid until: {_safe(row['digital_id_expires_at'])[:10]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.image(_qr_bytes(row["digital_id_token"]), caption="Secure verification QR", width=190)
    with c2:
        st.image(_barcode_bytes(row["digital_staff_id"]), caption="Code 128 staff barcode", width=320)


def show_digital_id_centre(current_operator_id=None, super_admin=False):
    """Super Admin centre for issuing, viewing and verifying Digital Staff IDs."""
    ensure_staff_id_fields()
    st.title("🪪 Secure Digital Staff ID Centre")
    st.caption("Automatic staff identification, QR/barcode verification and ID lifecycle management.")

    tabs = st.tabs(["🪪 Staff IDs", "🔎 Security Scanner", "⚙️ ID Administration"])

    with tabs[0]:
        connection = get_connection()
        rows = connection.execute(
            "SELECT * FROM staff_users ORDER BY full_name COLLATE NOCASE"
        ).fetchall()
        connection.close()

        if not rows:
            st.info("No staff accounts found.")
            return

        st.info("Every staff member can have a permanent PIA Staff ID. Existing IDs are never replaced unless the Admin explicitly renews/regenerates the secure token.")
        for row in rows:
            with st.container(border=True):
                a, b, c, d = st.columns([3, 2, 2, 1])
                with a:
                    st.write(f"**{row['full_name']}**")
                    st.caption(f"{row['role']} • {row['department'] if 'department' in row.keys() else ''}")
                with b:
                    st.write(f"🪪 {row['digital_staff_id'] or 'Not issued'}")
                    st.caption(f"ID status: {row['digital_id_status'] or 'Not issued'}")
                with c:
                    if row['digital_id_expires_at']:
                        st.caption(f"Expires: {row['digital_id_expires_at'][:10]}")
                    if row['digital_id_token']:
                        st.caption("Secure token: present")
                with d:
                    if not row['digital_staff_id']:
                        if st.button("Generate", key=f"issue_id_{row['id']}", use_container_width=True):
                            ok, message = issue_digital_id(row['id'])
                            if ok:
                                st.success(message)
                                st.rerun()
                    else:
                        if st.button("View", key=f"view_id_{row['id']}", use_container_width=True):
                            st.session_state["digital_id_selected"] = row['id']

        selected_id = st.session_state.get("digital_id_selected")
        if selected_id:
            selected = get_staff_id_record(selected_id)
            if selected:
                st.divider()
                st.subheader("🪪 Digital ID Preview")
                _render_card(selected)
                pdf = build_id_pdf(selected)
                st.download_button(
                    "📄 Download Printable PDF ID",
                    data=pdf,
                    file_name=f"{selected['digital_staff_id']}_digital_id.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

    with tabs[1]:
        st.subheader("🔎 Security Entrance Verification")
        st.write("Use a USB barcode scanner, QR scanner, or type the Staff ID manually. Most USB scanners behave like a keyboard and work directly in this box.")
        scan_value = st.text_input(
            "Scan Staff ID / QR token",
            key="pia_security_scan_value",
            placeholder="Scan PIA-STAFF-0001 here...",
        )
        if scan_value:
            row, message = verify_staff_identity(scan_value)
            if row and message.startswith("ACCESS GRANTED"):
                st.success(message)
                c1, c2, c3 = st.columns(3)
                c1.metric("Staff", row["full_name"])
                c2.metric("Department", row["department"] if "department" in row.keys() and row["department"] else "—")
                c3.metric("Staff ID", row["digital_staff_id"])
                st.info("🟢 Security officer may permit entry. The access event can be connected to the Audit Log in the next security phase.")
            else:
                st.error(message)
                if row:
                    st.warning(f"Matched record: {row['full_name']} • {row['digital_staff_id'] or 'No ID'}")

    with tabs[2]:
        if not super_admin:
            st.warning("Only the Super Admin can change Digital ID issuance or revocation settings.")
            return

        st.subheader("⚙️ ID Administration")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✨ Generate IDs for All Existing Staff", use_container_width=True, type="primary"):
                results = ensure_all_staff_ids()
                st.success(f"Checked {len(results)} staff account(s). Existing IDs were preserved and missing IDs were generated.")
                st.rerun()
        with c2:
            st.caption("ID numbers are permanent. The secure QR token can be renewed without changing the staff ID number.")

        connection = get_connection()
        rows = connection.execute("SELECT * FROM staff_users ORDER BY full_name COLLATE NOCASE").fetchall()
        connection.close()
        for row in rows:
            if row['digital_staff_id']:
                with st.expander(f"{row['digital_staff_id']} — {row['full_name']}"):
                    x, y, z = st.columns(3)
                    with x:
                        if st.button("🔄 Renew Secure Token", key=f"renew_id_{row['id']}"):
                            ok, message = issue_digital_id(row['id'], force=True)
                            if ok:
                                st.success(f"Renewed {message}")
                                st.rerun()
                    with y:
                        if st.button("🚫 Revoke ID", key=f"revoke_id_{row['id']}"):
                            ok, message = revoke_digital_id(row['id'])
                            if ok:
                                st.success(message)
                                st.rerun()
                    with z:
                        st.caption(f"Version {row['digital_id_version'] or 1}")
                        st.caption(f"Status: {row['digital_id_status'] or 'Unknown'}")

def answer_business(question):
    """
    Business knowledge assistant for the Pan Ideate Africa Business Suite.
    Returns a focused answer based on the user's question.
    """

    q = question.lower().strip()

    # BUSINESS DEVELOPMENT
    if any(word in q for word in [
        "business development",
        "develop a business",
        "start a business",
        "business idea",
        "entrepreneurship",
        "entrepreneur"
    ]):
        return """
### 💼 Business Development

The Pan Ideate Africa Business Suite helps users transform
scientific knowledge, local resources and innovative ideas
into practical businesses.

The approach is:

**Learn → Innovate → Produce → Manage → Sell → Prosper**

The goal is to connect science and innovation with practical
entrepreneurship.
"""

    # MARKETPLACE
    if any(word in q for word in [
        "marketplace",
        "sell products",
        "selling products",
        "sell",
        "customers"
    ]):
        return """
### 🛒 Marketplace

The Pan Ideate Africa Marketplace is intended to help
entrepreneurs present and sell products and services
across Uganda and Africa.

It can support businesses producing products such as
Biochar, Kaolin, Iron Oxide Pigments, Bentonite products
and agricultural products.
"""

    # INVENTORY
    if any(word in q for word in [
        "inventory",
        "stock",
        "stock management",
        "stock levels",
        "low stock"
    ]):
        return """
### 📦 Inventory Management

Inventory Management helps a business monitor:

• Stock levels
• Production
• Available products
• Low-stock situations

Its purpose is to help entrepreneurs know what they have,
what has been produced and when stock needs attention.
"""

    # SALES
    if any(word in q for word in [
        "sales",
        "sales management",
        "track sales",
        "daily sales",
        "weekly sales",
        "monthly sales"
    ]):
        return """
### 📈 Sales Management

Sales Management is intended to help businesses track
their daily, weekly and monthly sales.

This can help entrepreneurs understand sales performance
and monitor business growth.
"""

    # CUSTOMER MANAGEMENT
    if any(word in q for word in [
        "customer management",
        "customers",
        "customer information",
        "purchase history"
    ]):
        return """
### 👥 Customer Management

Customer Management helps businesses store customer
information and purchase history.

This can help entrepreneurs keep better records of
their customers and transactions.
"""

    # INVOICES
    if any(word in q for word in [
        "invoice",
        "invoices",
        "receipt",
        "receipts",
        "quotation",
        "quotations"
    ]):
        return """
### 🧾 Invoice & Receipt Generator

The Business Suite is designed to support the creation
of:

• Quotations
• Invoices
• Receipts

These tools help businesses document transactions
professionally.
"""

    # EMPLOYEES
    if any(word in q for word in [
        "employee",
        "employees",
        "staff",
        "attendance",
        "employee management"
    ]):
        return """
### 👨‍💼 Employee Management

Employee Management helps businesses organize:

• Staff records
• Employee information
• Attendance

This provides a structured way of managing business staff.
"""

    # EXPENSES
    if any(word in q for word in [
        "expense",
        "expenses",
        "business costs",
        "costs",
        "spending"
    ]):
        return """
### 💰 Expense Management

Expense Management helps entrepreneurs monitor business
costs and understand where money is being spent.

Tracking expenses is important for understanding business
performance and profitability.
"""

    # BUSINESS PRODUCTS
    if any(word in q for word in [
        "products",
        "business products",
        "what can i produce",
        "what can i sell",
        "product business"
    ]):
        return """
### 🏭 Business Product Opportunities

The Pan Ideate Africa Business Suite can support businesses
based on:

• Biochar
• Kaolin
• Iron Oxide Pigments
• Bentonite Products
• Agricultural Products
• Mineral-based products
• Other scientific and innovative products

These opportunities connect the Knowledge Hub's scientific
and agricultural knowledge with entrepreneurship.
"""

    # MARKET INTELLIGENCE
    if any(word in q for word in [
        "market intelligence",
        "market research",
        "market",
        "customers",
        "market opportunity"
    ]):
        return """
### 📊 Market Intelligence

Market Intelligence is intended to help entrepreneurs
understand:

• Customers
• Markets
• Products
• Business opportunities

This information can support better business planning
and decision-making.
"""

    # BUSINESS PLANNING
    if any(word in q for word in [
        "business plan",
        "business planning",
        "plan a business",
        "business strategy"
    ]):
        return """
### 📋 Business Planning

Business Planning helps transform an idea into a structured
business opportunity.

A good business plan should connect the product or service
with production, customers, markets, costs and revenue.
"""

    # INVESTMENT
    if any(word in q for word in [
        "investment",
        "investor",
        "investors",
        "funding",
        "capital"
    ]):
        return """
### 💎 Investment

The Pan Ideate Africa Business Suite is intended to provide
investor-oriented resources and help promising African
innovations become more investment-ready.

The aim is to connect strong scientific and innovative ideas
with appropriate business development and investment
opportunities.
"""

    # BUSINESS SUITE OVERVIEW
    if any(word in q for word in [
        "business suite",
        "business areas",
        "business features",
        "what does the business suite do",
        "what is the business suite"
    ]):
        return """
### 💼 Pan Ideate Africa Business Suite

The Business Suite connects scientific knowledge,
innovation and entrepreneurship to practical business
development.

Its major areas include:

1. Business Development
2. Marketplace
3. Inventory Management
4. Sales Management
5. Customer Management
6. Invoice & Receipt Generation
7. Employee Management
8. Expense Management
9. Market Intelligence
10. Business Planning
11. Investment

Business model:

**Learn → Innovate → Produce → Manage → Sell → Prosper**
"""

    # DEFAULT BUSINESS RESPONSE
    return """
### 💼 Pan Ideate Africa Business Assistant

I can currently help with questions about:

• Business Development
• Marketplace
• Inventory Management
• Sales Management
• Customer Management
• Invoices and Receipts
• Employee Management
• Expense Management
• Business Products
• Market Intelligence
• Business Planning
• Investment

Try asking a specific question, for example:

**"What is inventory management?"**

or

**"How does the Marketplace work?"**
"""
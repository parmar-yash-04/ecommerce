<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Commerce Backend API</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; color: #333; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        h3 { color: #7f8c8d; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
        pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
        table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background: #3498db; color: white; }
        tr:nth-child(even) { background: #f9f9f9; }
        ul { padding-left: 20px; }
        li { margin: 8px 0; }
        .badge { display: inline-block; background: #3498db; color: white; padding: 3px 10px; border-radius: 15px; font-size: 0.85em; margin-right: 5px; }
        .note { background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px 15px; margin: 15px 0; }
    </style>
</head>
<body>

<h1>E-Commerce Backend API</h1>

<p>A FastAPI-based RESTful API for an e-commerce platform with user authentication, product management, cart, wishlist, and order processing.</p>

<h2>Tech Stack</h2>
<ul>
    <li><span class="badge">FastAPI</span> Python web framework</li>
    <li><span class="badge">PostgreSQL</span> Database</li>
    <li><span class="badge">SQLAlchemy</span> ORM</li>
    <li><span class="badge">JWT</span> Authentication</li>
    <li><span class="badge">Alembic</span> Database Migrations</li>
</ul>

<h2>Features</h2>
<ul>
    <li>User registration and management</li>
    <li>JWT-based authentication</li>
    <li>Product catalog with categories</li>
    <li>Shopping cart functionality</li>
    <li>Wishlist management</li>
    <li>OTP-based phone verification</li>
    <li>Checkout and order processing</li>
    <li>Order tracking</li>
</ul>

<h2>Prerequisites</h2>
<ul>
    <li>Python 3.8+</li>
    <li>PostgreSQL (local or cloud)</li>
</ul>

<h2>Installation</h2>

<h3>1. Clone the repository</h3>
<pre><code>git clone &lt;your-repo-url&gt;
cd Ecommerce</code></pre>

<h3>2. Create a virtual environment</h3>
<pre><code>python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate</code></pre>

<h3>3. Install dependencies</h3>
<pre><code>pip install -r requirements.txt</code></pre>

<h3>4. Configure environment variables</h3>
<p>Create a <code>.env</code> file in the root directory:</p>
<pre><code>DATABASE_URL=postgresql://postgres:&lt;password&gt;@localhost:5432/ecommerce
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30</code></pre>

<div class="note">
<strong>Note:</strong> Replace the placeholder values with your actual configuration. Never commit the <code>.env</code> file to version control.
</div>

<h3>5. Run database migrations</h3>
<pre><code>alembic upgrade head</code></pre>

<h3>6. Start the server</h3>
<pre><code>uvicorn main:app --reload</code></pre>
<p>The API will be available at <code>http://127.0.0.1:8000</code></p>

<h3>7. Access API documentation</h3>
<ul>
    <li>Swagger UI: <a href="http://127.0.0.1:8000/docs">http://127.0.0.1:8000/docs</a></li>
    <li>ReDoc: <a href="http://127.0.0.1:8000/redoc">http://127.0.0.1:8000/redoc</a></li>
</ul>

<h2>Deployment (Render)</h2>

<p>This project is configured for deployment on <a href="https://render.com/" target="_blank">Render</a>.</p>

<h3>Automatic Deploy (Recommended)</h3>
<ol>
    <li>Push your code to GitHub</li>
    <li>Create a new Web Service on Render</li>
    <li>Connect your GitHub repository</li>
    <li>Render will automatically:
        <ul>
            <li>Create the <code>ecommerce-db</code> PostgreSQL database</li>
            <li>Set the <code>DATABASE_URL</code> environment variable</li>
            <li>Install dependencies and start the server</li>
        </ul>
    </li>
</ol>

<h3>Using render.yaml</h3>
<p>The <code>render.yaml</code> file in this repository defines the required infrastructure:</p>
<pre><code>render deploy</code></pre>
<p>This will create:</p>
<ul>
    <li>Web service: <code>ecommerce-api</code></li>
    <li>PostgreSQL database: <code>ecommerce-db</code></li>
</ul>

<h3>Environment Variables on Render</h3>
<p>The following environment variables are automatically configured:</p>

<table>
    <tr>
        <th>Variable</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><code>DATABASE_URL</code></td>
        <td>PostgreSQL connection string (auto-generated)</td>
    </tr>
    <tr>
        <td><code>SECRET_KEY</code></td>
        <td>Auto-generated JWT secret key</td>
    </tr>
    <tr>
        <td><code>ALGORITHM</code></td>
        <td>JWT algorithm (HS256)</td>
    </tr>
    <tr>
        <td><code>ACCESS_TOKEN_EXPIRE_MINUTES</code></td>
        <td>Token expiration time (30)</td>
    </tr>
</table>

<h2>API Endpoints</h2>

<h3>Authentication</h3>
<table>
    <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
    <tr><td>POST</td><td><code>/auth/register</code></td><td>Register new user</td></tr>
    <tr><td>POST</td><td><code>/auth/login</code></td><td>Login and get JWT token</td></tr>
</table>

<h3>Users</h3>
<table>
    <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
    <tr><td>GET</td><td><code>/users/me</code></td><td>Get current user profile</td></tr>
    <tr><td>PUT</td><td><code>/users/me</code></td><td>Update user profile</td></tr>
</table>

<h3>Products</h3>
<table>
    <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
    <tr><td>GET</td><td><code>/products/</code></td><td>List all products</td></tr>
    <tr><td>GET</td><td><code>/products/{id}</code></td><td>Get product details</td></tr>
    <tr><td>POST</td><td><code>/products/</code></td><td>Create product (admin)</td></tr>
    <tr><td>PUT</td><td><code>/products/{id}</code></td><td>Update product</td></tr>
    <tr><td>DELETE</td><td><code>/products/{id}</code></td><td>Delete product</td></tr>
</table>

<h3>Cart</h3>
<table>
    <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
    <tr><td>GET</td><td><code>/cart/</code></td><td>Get user cart</td></tr>
    <tr><td>POST</td><td><code>/cart/</code></td><td>Add item to cart</td></tr>
    <tr><td>PUT</td><td><code>/cart/{id}</code></td><td>Update cart item</td></tr>
    <tr><td>DELETE</td><td><code>/cart/{id}</code></td><td>Remove item from cart</td></tr>
</table>

<h3>Wishlist</h3>
<table>
    <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
    <tr><td>GET</td><td><code>/wishlist/</code></td><td>Get user wishlist</td></tr>
    <tr><td>POST</td><td><code>/wishlist/</code></td><td>Add item to wishlist</td></tr>
    <tr><td>DELETE</td><td><code>/wishlist/{id}</code></td><td>Remove item from wishlist</td></tr>
</table>

<h3>Orders</h3>
<table>
    <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
    <tr><td>GET</td><td><code>/orders/</code></td><td>Get user orders</td></tr>
    <tr><td>POST</td><td><code>/orders/</code></td><td>Create new order</td></tr>
    <tr><td>GET</td><td><code>/orders/{id}</code></td><td>Get order details</td></tr>
</table>

<h2>Project Structure</h2>
<pre><code>Ecommerce/
├── app/
│   ├── router/          # API route handlers
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── products.py
│   │   ├── cart.py
│   │   ├── wishlist.py
│   │   ├── checkout.py
│   │   └── orders.py
│   ├── config.py        # Configuration
│   ├── database.py      # Database connection
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── oauth2.py        # JWT authentication
│   └── utils.py         # Utility functions
├── alembic/             # Database migrations
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── render.yaml          # Render deployment config
└── .env.example         # Environment variables template</code></pre>

<h2>License</h2>
<p>MIT License</p>

</body>
</html>

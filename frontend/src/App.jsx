import { useEffect, useState } from 'react'
import {
  Utensils, Search, MapPin, ArrowLeft, Plus, RefreshCw,
  ShoppingCart, X, Minus, Trash2, LogOut, User
} from 'lucide-react'
import './App.css'

const API = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '')

const formatINR = (amount) =>
  `\u20B9${new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(amount || 0))}`


function App() {
  const [restaurants, setRestaurants] = useState([])
  const [menu, setMenu] = useState([])
  const [selected, setSelected] = useState(null)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [token, setToken] = useState(() => sessionStorage.getItem('mealflow_token') || '')
  const [cart, setCart] = useState(null)
  const [orders, setOrders] = useState([])
  const [showOrders, setShowOrders] = useState(false)
  const [checkoutLoading, setCheckoutLoading] = useState(false)
  const [showCart, setShowCart] = useState(false)
  const [showAuth, setShowAuth] = useState(false)
  const [authMode, setAuthMode] = useState('login')
  const [authData, setAuthData] = useState({ name: '', email: '', password: '' })
  const [authError, setAuthError] = useState('')
  const [authLoading, setAuthLoading] = useState(false)
  const [toast, setToast] = useState('')

  async function apiRequest(path, options = {}, authToken = token) {
    const headers = { ...options.headers }
    if (options.body) headers['Content-Type'] = 'application/json'
    if (authToken) headers.Authorization = `Bearer ${authToken}`

    const response = await fetch(`${API}${path}`, { ...options, headers })
    const data = await response.json().catch(() => null)

    if (!response.ok) {
      const detail = data?.detail
      let message = 'Something went wrong'

      if (typeof detail === 'string') {
        message = detail
      } else if (Array.isArray(detail)) {
        message = detail.map((item) =>
          item.msg || item.message || JSON.stringify(item)
        ).join(', ')
      } else if (detail && typeof detail === 'object') {
        message = detail.message || JSON.stringify(detail)
      }

      throw new Error(message)
    }

    return data
  }

  function notify(message) {
    setToast(message)
    window.setTimeout(() => setToast(''), 2500)
  }

  async function loadRestaurants() {
    setLoading(true)
    setError('')
    try {
      const data = await apiRequest('/restaurants/')
      setRestaurants(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function openRestaurant(restaurant) {
    setSelected(restaurant)
    setShowCart(false)
    setLoading(true)
    setError('')
    try {
      const data = await apiRequest(`/menu/?restaurant_id=${restaurant.id}`)
      setMenu(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message)
      setMenu([])
    } finally {
      setLoading(false)
    }
  }

  async function loadCart(authToken = token) {
    if (!authToken) return
    try {
      const data = await apiRequest('/cart/', {}, authToken)
      setCart(data)
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleAuth(event) {
    event.preventDefault()
    setAuthError('')
    setAuthLoading(true)

    try {
      if (authMode === 'register') {
        await apiRequest('/users/register', {
          method: 'POST',
          body: JSON.stringify(authData),
        }, '')
      }

      const loginData = await apiRequest('/users/login', {
        method: 'POST',
        body: JSON.stringify({
          email: authData.email,
          password: authData.password,
        }),
      }, '')

      sessionStorage.setItem('mealflow_token', loginData.access_token)
      setToken(loginData.access_token)
      await loadCart(loginData.access_token)
      setShowAuth(false)
      setAuthData({ name: '', email: '', password: '' })
      notify(authMode === 'register' ? 'Account created successfully!' : 'Welcome back!')
    } catch (err) {
      setAuthError(err.message)
    } finally {
      setAuthLoading(false)
    }
  }

  function logout() {
    sessionStorage.removeItem('mealflow_token')
    setToken('')
    setCart(null)
    setShowCart(false)
    notify('Logged out successfully')
  }

  async function addToCart(item) {
    if (!token) {
      setAuthMode('login')
      setShowAuth(true)
      return
    }

    try {
      const data = await apiRequest('/cart/items', {
        method: 'POST',
        body: JSON.stringify({ menu_item_id: item.id, quantity: 1 }),
      })
      setCart(data)
      notify(`${item.name} added to cart`)
    } catch (err) {
      setError(err.message)
    }
  }

  async function updateQuantity(cartItem, quantity) {
    try {
      const data = quantity <= 0
        ? await apiRequest(`/cart/items/${cartItem.id}`, { method: 'DELETE' })
        : await apiRequest(`/cart/items/${cartItem.id}`, {
            method: 'PATCH',
            body: JSON.stringify({ quantity }),
          })
      setCart(data)
    } catch (err) {
      setError(err.message)
    }
  }

  async function checkout() {
    setCheckoutLoading(true)
    setError('')
    try {
      const order = await apiRequest('/orders/checkout', {
        method: 'POST'
      })
      setCart(null)
      notify(`Order #${order.id} placed successfully!`)
      await loadOrders()
      setShowCart(false)
      setShowOrders(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setCheckoutLoading(false)
    }
  }

  async function loadOrders() {
    try {
      const data = await apiRequest('/orders/')
      setOrders(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message)
    }
  }

  async function cancelOrder(orderId) {
    try {
      await apiRequest(`/orders/${orderId}/cancel`, {
        method: 'PATCH'
      })
      notify(`Order #${orderId} cancelled`)
      await loadOrders()
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    loadRestaurants()
    if (token) loadCart(token)
  }, [])

  const filteredRestaurants = restaurants.filter((restaurant) =>
    restaurant.name?.toLowerCase().includes(search.toLowerCase()) ||
    restaurant.address?.toLowerCase().includes(search.toLowerCase())
  )

  const cartItems = cart?.items || []

  return (
    <div className="app">
      <header className="navbar">
        <div className="nav-inner">
          <button className="brand" onClick={() => {
            setSelected(null)
            setShowCart(false)
            setShowOrders(false)
            setError('')
          }}>
            <span className="brand-icon"><Utensils size={21} /></span>
            Meal<span>Flow</span>
          </button>

          <nav className="nav-links">
            <button onClick={() => {
              setSelected(null)
              setShowCart(false)
              setShowOrders(false)
            }}>Discover</button>
          </nav>

          <div className="nav-actions">
            <span className="eyebrow">FRESH FOOD, EVERY DAY</span>
            {token ? (
              <>
                <button className="cart-button" onClick={() => {
                  setShowOrders(false)
                  setShowCart(false)
                  setSelected(null)
                  loadOrders()
                  setShowOrders(true)
                }}>
                  Orders
                </button>
                <button className="cart-button" onClick={() => {
                  setShowOrders(false)
                  setShowCart(true)
                  setSelected(null)
                  loadCart()
                }}>
                  <ShoppingCart size={17} /> Cart ({cartItems.length})
                </button>
                <button className="login-button" onClick={logout}>
                  <LogOut size={16} /> Logout
                </button>
              </>
            ) : (
              <button className="login-button" onClick={() => {
                setAuthMode('login')
                setShowAuth(true)
              }}>
                <User size={16} /> Login
              </button>
            )}
          </div>
        </div>
      </header>

      {showOrders ? (
        <main className="page-container">
          <button className="back-button" onClick={() => setShowOrders(false)}>
            <ArrowLeft size={16} /> Continue browsing
          </button>

          <div className="page-title">
            <span className="eyebrow">YOUR MEALFLOW ACTIVITY</span>
            <h1>My orders</h1>
            <p>Track your previous orders.</p>
          </div>

          {error && <p className="error-message">{error}</p>}

          {!orders.length ? (
            <div className="empty-state">
              <ShoppingCart size={35} />
              <h3>No orders yet</h3>
              <p>Your placed orders will appear here.</p>
            </div>
          ) : (
            <div className="orders-list">
              {orders.map((order) => (
                <article className="order-card" key={order.id}>
                  <div>
                    <h3>Order #{order.id}</h3>
                    <p className="order-date">
                      {order.created_at
                        ? new Date(order.created_at).toLocaleString()
                        : ''}
                    </p>
                  </div>

                  <span className={`status status-${order.status}`}>
                    {order.status}
                  </span>

                  <div className="order-items">
                    {(order.items || []).map((item) => (
                      <div className="order-item-row" key={item.id}>
                        <span className="order-item-name">
                          <strong>{item.menu_item?.name || `Menu item #${item.menu_item_id}`}</strong>
                          <small>{item.quantity} ? {formatINR(item.price)}</small>
                        </span>
                        <strong className="order-item-price">
                          {formatINR(Number(item.price) * item.quantity)}
                        </strong>
                      </div>
                    ))}
                  </div>

                  <div className="summary-line">
                    <strong>Total</strong>
                    <strong>{formatINR(order.total_amount)}</strong>
                  </div>

                  {order.status === 'placed' && (
                    <button
                      className="cancel-button"
                      onClick={() => cancelOrder(order.id)}
                    >
                      Cancel order
                    </button>
                  )}
                </article>
              ))}
            </div>
          )}
        </main>
      ) : showCart ? (
        <main className="page-container">
          <button className="back-button" onClick={() => setShowCart(false)}>
            <ArrowLeft size={16} /> Continue browsing
          </button>

          <div className="page-title">
            <span className="eyebrow">YOUR SELECTION</span>
            <h1>Your cart</h1>
            <p>Review your items before checkout.</p>
          </div>

          {error && <p className="error-message">{error}</p>}

          {!cartItems.length ? (
            <div className="empty-state">
              <ShoppingCart size={35} />
              <h3>Your cart is empty</h3>
              <p>Discover restaurants and add something delicious.</p>
              <button className="text-button" onClick={() => setShowCart(false)}>
                Explore restaurants
              </button>
            </div>
          ) : (
            <div className="cart-layout">
              <div className="cart-items">
                {cartItems.map((item) => (
                  <article className="cart-item" key={item.id}>
                    <div className="cart-food-icon">🍽️</div>
                    <div className="cart-item-info">
                      <h3>{item.menu_item?.name || 'Menu item'}</h3>
                      <p>₹{Number(item.menu_item?.price || 0).toFixed(2)}</p>
                      <div className="quantity-control">
                        <button onClick={() => updateQuantity(item, item.quantity - 1)}>
                          <Minus size={14} />
                        </button>
                        <span>{item.quantity}</span>
                        <button onClick={() => updateQuantity(item, item.quantity + 1)}>
                          <Plus size={14} />
                        </button>
                      </div>
                    </div>
                    <div className="line-total">
                      <strong>₹{Number(item.subtotal || 0).toFixed(2)}</strong>
                      <button className="remove-button" onClick={() => updateQuantity(item, 0)}>
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </article>
                ))}
              </div>

              <aside className="order-summary">
                <h2>Order summary</h2>
                <div className="summary-line">
                  <span>Items ({cartItems.length})</span>
                  <strong>₹{Number(cart.total_amount || 0).toFixed(2)}</strong>
                </div>
                <div className="summary-line">
                  <span>Delivery</span>
                  <strong>Calculated at checkout</strong>
                </div>
                <div className="summary-line">
                  <strong>Total</strong>
                  <strong>₹{Number(cart.total_amount || 0).toFixed(2)}</strong>
                </div>
                <button className="checkout-button"
                  onClick={checkout}
                  disabled={checkoutLoading || !cartItems.length}>
                  {checkoutLoading ? 'Placing order...' : 'Place order'}
                </button>
              </aside>
            </div>
          )}
        </main>
      ) : !selected ? (
        <main>
          <section className="hero">
            <div className="hero-content">
              <span className="eyebrow">GOOD FOOD, GOOD MOOD</span>
              <h1>Your next<br />favourite meal<br /><em>is waiting.</em></h1>
              <p>Discover great restaurants and explore delicious food.</p>
              <button className="primary-button" onClick={() =>
                document.getElementById('restaurants')?.scrollIntoView({ behavior: 'smooth' })
              }>
                Explore restaurants
              </button>
            </div>
            <div className="hero-art">
              <div className="hero-circle"><span>🍜</span></div>
              <div className="floating-card">
                <span>⭐</span>
                <div><strong>Made fresh</strong><small>Just for you</small></div>
              </div>
            </div>
          </section>

          <section className="restaurant-section" id="restaurants">
            <div className="section-heading">
              <div>
                <span className="eyebrow">EXPLORE THE TASTE</span>
                <h2>Restaurants near you</h2>
                <p>Find something delicious today.</p>
              </div>
              <div className="search-box">
                <Search size={18} />
                <input
                  placeholder="Search restaurants..."
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />
              </div>
            </div>

            {error && <p className="error-message">{error}</p>}
            {loading ? (
              <div className="loading-state">Loading restaurants...</div>
            ) : (
              <div className="restaurant-grid">
                {filteredRestaurants.map((restaurant, index) => (
                  <button className="restaurant-card" key={restaurant.id}
                    onClick={() => openRestaurant(restaurant)}>
                    <div className={`restaurant-art art-${index % 4}`}>
                      <span>{['🍕', '🍔', '🍜', '🥗'][index % 4]}</span>
                      <small>MEALFLOW PICKS</small>
                    </div>
                    <div className="restaurant-info">
                      <div>
                        <h3>{restaurant.name}</h3>
                        <p><MapPin size={13} /> {restaurant.address || 'Great food, great taste'}</p>
                      </div>
                      <span className="card-arrow">↗</span>
                    </div>
                  </button>
                ))}
                {!filteredRestaurants.length && (
                  <div className="empty-state">
                    <Utensils size={35} />
                    <h3>No restaurants found</h3>
                    <p>Try another search or refresh the list.</p>
                    <button className="text-button" onClick={loadRestaurants}>
                      <RefreshCw size={14} /> Refresh
                    </button>
                  </div>
                )}
              </div>
            )}
          </section>
        </main>
      ) : (
        <main className="page-container">
          <button className="back-button" onClick={() => setSelected(null)}>
            <ArrowLeft size={16} /> Back to restaurants
          </button>
          <div className="page-title">
            <span className="eyebrow">EXPLORE THE MENU</span>
            <h1>{selected.name}</h1>
            <p>{selected.address}</p>
          </div>
          {error && <p className="error-message">{error}</p>}
          {loading ? (
            <div className="loading-state">Loading menu...</div>
          ) : (
            <div className="menu-grid">
              {menu.map((item, index) => (
                <article className="menu-card" key={item.id}>
                  <div className={`menu-art art-${index % 4}`}>
                    <span>{['🍛', '🍝', '🥘', '🍰'][index % 4]}</span>
                  </div>
                  <div className="menu-info">
                    <h3>{item.name}</h3>
                    <p>{item.description || 'Freshly prepared and full of flavour.'}</p>
                    <div className="menu-bottom">
                      <strong>₹{Number(item.price).toFixed(2)}</strong>
                      <button className="add-button"
                        disabled={item.is_available === false}
                        onClick={() => addToCart(item)}>
                        <Plus size={16} /> Add
                      </button>
                    </div>
                  </div>
                </article>
              ))}
              {!menu.length && (
                <div className="empty-state">
                  <Utensils size={35} />
                  <h3>No menu items available</h3>
                  <p>This restaurant hasn't added its menu yet.</p>
                </div>
              )}
            </div>
          )}
        </main>
      )}

      {showAuth && (
        <div className="modal-backdrop" onClick={() => setShowAuth(false)}>
          <div className="auth-modal" onClick={(event) => event.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowAuth(false)}>
              <X size={19} />
            </button>
            <div className="auth-logo"><Utensils size={24} /></div>
            <h2>{authMode === 'login' ? 'Welcome back' : 'Create your account'}</h2>
            <p>{authMode === 'login' ? 'Log in to continue to MealFlow.' : 'Join MealFlow and discover great food.'}</p>

            <form onSubmit={handleAuth}>
              {authMode === 'register' && (
                <input
                  placeholder="Full name"
                  value={authData.name}
                  onChange={(event) => setAuthData({ ...authData, name: event.target.value })}
                  required
                />
              )}
              <input
                type="email"
                placeholder="Email address"
                value={authData.email}
                onChange={(event) => setAuthData({ ...authData, email: event.target.value })}
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={authData.password}
                onChange={(event) => setAuthData({ ...authData, password: event.target.value })}
                required
              />
              {authError && <p className="error-message">{authError}</p>}
              <button className="checkout-button" type="submit" disabled={authLoading}>
                {authLoading ? 'Please wait...' : authMode === 'login' ? 'Login' : 'Create account'}
              </button>
            </form>

            <p className="auth-switch">
              {authMode === 'login' ? "Don't have an account?" : 'Already have an account?'}
              <button onClick={() => {
                setAuthMode(authMode === 'login' ? 'register' : 'login')
                setAuthError('')
              }}>
                {authMode === 'login' ? 'Register' : 'Login'}
              </button>
            </p>
          </div>
        </div>
      )}

      {toast && <div className="toast">{toast}</div>}

      <footer>
        <button className="brand footer-brand" onClick={() => {
          setSelected(null)
          setShowCart(false)
        }}>
          <span className="brand-icon"><Utensils size={18} /></span>
          Meal<span>Flow</span>
        </button>
        <p>Good food. Great moments. Delivered.</p>
        <span>© 2026 MealFlow</span>
      </footer>
    </div>
  )
}

export default App

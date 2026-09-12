import { useMemo, useState } from "react";
import { ArrowRight, ChevronDown, Clock3, Heart, MapPin, Search, ShoppingBag, Star, Sparkles, Utensils } from "lucide-react";

const restaurants = [
  { name: "Namma Thindi", cuisine: "South Indian · Breakfast", rating: "4.8", time: "24 min", price: "₹₹", tag: "Pure veg", image: "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=900&q=85" },
  { name: "The Green Table", cuisine: "Healthy · Bowls", rating: "4.7", time: "31 min", price: "₹₹₹", tag: "20% off", image: "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=85" },
  { name: "Dilli Se", cuisine: "North Indian · Kebabs", rating: "4.6", time: "36 min", price: "₹₹", tag: "Top rated", image: "https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=900&q=85" },
  { name: "Crust & Craft", cuisine: "Pizza · Italian", rating: "4.5", time: "29 min", price: "₹₹₹", tag: "Free delivery", image: "https://images.unsplash.com/photo-1579751626657-72bc17010498?auto=format&fit=crop&w=900&q=85" },
];

const categories = [
  ["Biryani", "🍛"], ["Pizza", "🍕"], ["South Indian", "🥘"], ["Burgers", "🍔"], ["Desserts", "🍰"], ["Beverages", "🧋"],
];

export function App() {
  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");
  const [favorites, setFavorites] = useState<string[]>([]);
  const [cartCount, setCartCount] = useState(0);

  const visibleRestaurants = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return restaurants.filter((restaurant) => {
      const matchesQuery = !normalized || `${restaurant.name} ${restaurant.cuisine}`.toLowerCase().includes(normalized);
      const matchesCategory = activeCategory === "All" || restaurant.cuisine.toLowerCase().includes(activeCategory.toLowerCase());
      return matchesQuery && matchesCategory;
    });
  }, [activeCategory, query]);

  function toggleFavorite(name: string) {
    setFavorites((current) => current.includes(name) ? current.filter((item) => item !== name) : [...current, name]);
  }

  return (
    <main className="app-shell">
      <nav className="topbar">
        <div className="brand"><span className="brand-mark"><Utensils size={17} /></span><span>FOODFLOW</span></div>
        <button className="location-button"><MapPin size={17} /><span><small>Delivering to</small>Indiranagar, Bengaluru</span><ChevronDown size={16} /></button>
        <div className="nav-actions"><button className="icon-button" aria-label="Favorites"><Heart size={19} /></button><button className="cart-button"><ShoppingBag size={18} /><span>Cart</span>{cartCount > 0 && <b>{cartCount}</b>}</button><button className="profile-button">AK</button></div>
      </nav>

      <section className="hero">
        <div className="hero-copy"><span className="eyebrow"><Sparkles size={14} /> Curated for your cravings</span><h1>Good food,<br /><em>good mood.</em></h1><p>Discover neighborhood favorites and have something wonderful at your door.</p>
          <label className="search-box"><Search size={20} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search for dishes, restaurants or cuisines" /><kbd>/</kbd></label>
        </div>
        <div className="hero-visual"><div className="hero-orbit orbit-one" /><div className="hero-orbit orbit-two" /><div className="plate"><img src="https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=700&q=90" alt="Fresh bowl with greens and grains" /></div><div className="floating-note"><Star size={15} fill="currentColor" /> <strong>4.9</strong><span>local favorites</span></div></div>
      </section>

      <section className="content-section category-section"><div className="section-heading"><div><span className="section-kicker">Explore the menu</span><h2>What are you in the mood for?</h2></div><button className="text-button">See all <ArrowRight size={16} /></button></div><div className="category-row"><button className={activeCategory === "All" ? "category active" : "category"} onClick={() => setActiveCategory("All")}><span>✦</span><small>Everything</small></button>{categories.map(([name, icon]) => <button key={name} className={activeCategory === name ? "category active" : "category"} onClick={() => setActiveCategory(name)}><span>{icon}</span><small>{name}</small></button>)}</div></section>

      <section className="content-section"><div className="section-heading"><div><span className="section-kicker">Picked for you</span><h2>Popular near you</h2></div><div className="sort-pill"><Clock3 size={15} /> Delivery time <ChevronDown size={14} /></div></div><div className="restaurant-grid">{visibleRestaurants.map((restaurant) => <article className="restaurant-card" key={restaurant.name}><div className="card-image"><img src={restaurant.image} alt={restaurant.name} /><span className="offer-tag">{restaurant.tag}</span><button className={favorites.includes(restaurant.name) ? "favorite active" : "favorite"} onClick={() => toggleFavorite(restaurant.name)} aria-label={`Favorite ${restaurant.name}`}><Heart size={18} fill={favorites.includes(restaurant.name) ? "currentColor" : "none"} /></button></div><div className="card-body"><div className="card-title"><h3>{restaurant.name}</h3><span className="rating"><Star size={13} fill="currentColor" /> {restaurant.rating}</span></div><p>{restaurant.cuisine}</p><div className="card-meta"><span>{restaurant.time}</span><span>·</span><span>{restaurant.price}</span><button onClick={() => setCartCount((count) => count + 1)}>Add to cart</button></div></div></article>)}</div>{visibleRestaurants.length === 0 && <div className="empty-state"><Search size={25} /><h3>No matches yet</h3><p>Try a different dish, cuisine, or restaurant.</p></div>}</section>

      <section className="content-section recommendation"><div><span className="section-kicker">Your taste profile</span><h2>Because you liked <em>Masala Dosa</em></h2><p>More crisp, comforting South Indian picks from kitchens nearby.</p></div><button className="outline-button">View recommendations <ArrowRight size={16} /></button></section>
      <footer><div className="brand"><span className="brand-mark"><Utensils size={15} /></span><span>FOODFLOW</span></div><span>Discover. Order. Track. Enjoy.</span><span>© 2026 Foodflow</span></footer>
    </main>
  );
}

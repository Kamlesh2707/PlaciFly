"""
Place Discovery Service — Smart Search, Filter & Recommendation Engine
Placifly Place Discovery Platform
"""

import re

PLACES_DATABASE = [
    {
        "id": "place-1",
        "name": "Nexus Horizon Tech Hub",
        "category": "Tech Park",
        "category_label": "Innovation & Tech Park",
        "location": "Whitefield, Bangalore",
        "city": "Bangalore",
        "rating": 4.9,
        "reviews_count": 428,
        "price_level": "$$$",
        "price_label": "₹15,000 / month",
        "distance": "2.4 km from center",
        "image": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80",
        "description": "World-class sustainable tech campus featuring high-speed 10Gbps fiber, ergonomic pods, enterprise meeting zones, and 24/7 security.",
        "amenities": ["10Gbps Fiber", "24/7 Power Backup", "EV Charging", "Cafeteria", "Podcast Studio", "Parking"],
        "tags": ["Technology", "Enterprise", "High Speed", "Modern"],
        "coordinates": {"lat": 12.9716, "lng": 77.5946}
    },
    {
        "id": "place-2",
        "name": "The Altitude Coworking Studio",
        "category": "Coworking Space",
        "category_label": "Premium Coworking",
        "location": "Cyber City, Gurugram",
        "city": "Gurugram",
        "rating": 4.8,
        "reviews_count": 312,
        "price_level": "$$",
        "price_label": "₹8,500 / month",
        "distance": "1.2 km from metro",
        "image": "https://images.unsplash.com/photo-1527192491265-7e15c55b1ed2?auto=format&fit=crop&w=800&q=80",
        "description": "Boutique rooftop creative space designed for startup founders, software creators, and designers with panoramic skyline views.",
        "amenities": ["High-Speed Wi-Fi", "Free Artisanal Coffee", "Standing Desks", "Meeting Rooms", "Rooftop Lounge"],
        "tags": ["Startup", "Design", "Networking", "Coffee"],
        "coordinates": {"lat": 28.4595, "lng": 77.0266}
    },
    {
        "id": "place-3",
        "name": "Silicon Cyber Vista",
        "category": "Tech Park",
        "category_label": "Software & AI Park",
        "location": "HITEC City, Hyderabad",
        "city": "Hyderabad",
        "rating": 4.9,
        "reviews_count": 560,
        "price_level": "$$$",
        "price_label": "₹18,000 / month",
        "distance": "0.8 km from Cyber Towers",
        "image": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80",
        "description": "Flagship technology development enclave housing premier software teams, AI testing labs, and high-frequency interview workstations.",
        "amenities": ["Ultra Low Latency", "Biometric Entry", "Auditorium", "Wellness Gym", "Food Court"],
        "tags": ["Software", "AI", "Cloud", "Placement Center"],
        "coordinates": {"lat": 17.4474, "lng": 78.3762}
    },
    {
        "id": "place-4",
        "name": "Coastal Nomad Workation Retreat",
        "category": "Workation",
        "category_label": "Travel & Workation",
        "location": "Anjuna, North Goa",
        "city": "Goa",
        "rating": 4.9,
        "reviews_count": 289,
        "price_level": "$$",
        "price_label": "₹2,200 / day",
        "distance": "300m from Beach",
        "image": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
        "description": "Tropical palm-fringed workation villa with backup generator, dedicated private work desks, infinity pool, and sunset networking decks.",
        "amenities": ["Fiber Wi-Fi", "Poolside Desks", "Yoga Deck", "Kitchen & Chef", "Surfboard Rental"],
        "tags": ["Workation", "Beach", "Travel", "Nomad"],
        "coordinates": {"lat": 15.5733, "lng": 73.7412}
    },
    {
        "id": "place-5",
        "name": "Quantum Innovation Campus",
        "category": "Placement Center",
        "category_label": "Campus & Placement Center",
        "location": "Electronic City, Bangalore",
        "city": "Bangalore",
        "rating": 4.7,
        "reviews_count": 340,
        "price_level": "$",
        "price_label": "₹500 / day pass",
        "distance": "Near Phase 1 Toll",
        "image": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=800&q=80",
        "description": "State-of-the-art campus learning facility with AI simulator testing bays, interview rooms, coding labs, and technical library.",
        "amenities": ["Mock Interview Rooms", "Coding Pods", "Hi-Speed LAN", "Library", "Cafeteria"],
        "tags": ["Student", "Interview Prep", "Campus", "Coding"],
        "coordinates": {"lat": 12.8399, "lng": 77.6770}
    },
    {
        "id": "place-6",
        "name": "Alpine Cloud Valley Retreat",
        "category": "Workation",
        "category_label": "Mountain Workation",
        "location": "Old Manali, Himachal Pradesh",
        "city": "Manali",
        "rating": 4.8,
        "reviews_count": 195,
        "price_level": "$$",
        "price_label": "₹2,500 / day",
        "distance": "Mountain View Point",
        "image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
        "description": "Serene Himalayan work escape surrounded by cedar forests, heated wooden workspaces, Starlink connectivity, and organic cafe.",
        "amenities": ["Starlink Satellite", "Heated Workspaces", "Mountain Trails", "Bonfire Lounge", "Organic Meals"],
        "tags": ["Mountains", "Nature", "Quiet", "Workation"],
        "coordinates": {"lat": 32.2432, "lng": 77.1892}
    },
    {
        "id": "place-7",
        "name": "Vertex Central Work Lounge",
        "category": "Work Cafe",
        "category_label": "Work Cafe & Lounge",
        "location": "Bandra Kurla Complex, Mumbai",
        "city": "Mumbai",
        "rating": 4.9,
        "reviews_count": 480,
        "price_level": "$$$",
        "price_label": "₹1,200 / day",
        "distance": "In Financial District",
        "image": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=800&q=80",
        "description": "Modern executive work cafe in Mumbai's premier business hub with private noise-cancelling pods, barista coffee, and rapid Wi-Fi.",
        "amenities": ["Noise-Proof Pods", "Specialty Coffee", "Valet Parking", "Meeting Screen", "High Speed"],
        "tags": ["Corporate", "Work Cafe", "Executive", "Mumbai"],
        "coordinates": {"lat": 19.0664, "lng": 72.8687}
    },
    {
        "id": "place-8",
        "name": "EcoSphere Tech Sanctum",
        "category": "Tech Park",
        "category_label": "Green Technology Campus",
        "location": "Kalyani Nagar, Pune",
        "city": "Pune",
        "rating": 4.8,
        "reviews_count": 270,
        "price_level": "$$",
        "price_label": "₹9,500 / month",
        "distance": "1.5 km from Airport Road",
        "image": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80",
        "description": "Zero-carbon tech workplace filled with natural indoor biophilic flora, open-air brainstorming decks, and advanced lab facilities.",
        "amenities": ["Solar Powered", "Indoor Garden", "Dedicated Desks", "Conference Suites", "Cafeteria"],
        "tags": ["Eco Friendly", "Tech Hub", "Pune", "Quiet"],
        "coordinates": {"lat": 18.5477, "lng": 73.9022}
    }
]


def search_places(query="", category="", city="", price_level="", min_rating=0.0, tags=None):
    """
    Search and filter places based on smart parameters.
    """
    results = PLACES_DATABASE.copy()
    
    if query:
        q = query.lower().strip()
        results = [
            p for p in results if (
                q in p['name'].lower() or
                q in p['location'].lower() or
                q in p['city'].lower() or
                q in p['category'].lower() or
                q in p['description'].lower() or
                any(q in t.lower() for t in p.get('tags', []))
            )
        ]
    
    if category and category.lower() != 'all':
        cat_lower = category.lower()
        results = [p for p in results if cat_lower in p['category'].lower() or cat_lower in p['category_label'].lower()]
        
    if city and city.lower() != 'all':
        results = [p for p in results if city.lower() in p['city'].lower()]
        
    if price_level and price_level.lower() != 'all':
        results = [p for p in results if p['price_level'] == price_level]
        
    if min_rating > 0:
        results = [p for p in results if p['rating'] >= min_rating]
        
    if tags:
        if isinstance(tags, str):
            tags = [t.strip().lower() for t in tags.split(',')]
        results = [p for p in results if any(t in [pt.lower() for pt in p.get('tags', [])] for t in tags)]
        
    return results


def get_place_by_id(place_id):
    for p in PLACES_DATABASE:
        if p['id'] == place_id:
            return p
    return None


def get_categories():
    return [
        {"id": "all", "label": "All Places", "icon": "✨"},
        {"id": "Tech Park", "label": "Tech Parks & HQs", "icon": "🏢"},
        {"id": "Coworking Space", "label": "Coworking Studios", "icon": "💼"},
        {"id": "Workation", "label": "Travel & Workations", "icon": "✈️"},
        {"id": "Placement Center", "label": "Campus & Placement", "icon": "🎓"},
        {"id": "Work Cafe", "label": "Work Cafes & Lounges", "icon": "☕"}
    ]

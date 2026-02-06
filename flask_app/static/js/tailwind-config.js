tailwind.config = {
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "primary": "#3b82f6",       // Modern Vibrant Blue
                "primary-hover": "#2563eb", // Darker blue for hover
                "brand-dark": "#1e293b",    // Slate 800
                "background-light": "#f1f5f9", // Slate 100
                "background-dark": "#020617",  // Slate 950 (Deep Void)
                "surface-dark": "#0f172a",     // Slate 900 (Cards)
                "accent": "#6366f1",        // Indigo
            },
            fontFamily: {
                "display": ["Inter", "sans-serif"]
            },
            borderRadius: {
                "DEFAULT": "0.25rem",
                "lg": "0.5rem",
                "xl": "0.75rem",
                "full": "9999px"
            },
        },
    },
}

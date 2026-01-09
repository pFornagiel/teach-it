/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "#fff6e5", // Updated Cream background
        foreground: "#000000",
        primary: {
          DEFAULT: "#8B5CF6", // Purple
          foreground: "#FFFFFF",
        },
        secondary: {
          DEFAULT: "#fde68a", // Yellow
          foreground: "#000000",
        },
        accent: {
          DEFAULT: "#fde68a", // Yellow (Unified)
          foreground: "#000000",
        },
        muted: {
          DEFAULT: "#E5E7EB",
          foreground: "#6B7280",
        },
        card: {
          DEFAULT: "#FFFFFF",
          foreground: "#000000",
        },
      },
      fontFamily: {
        sans: ["Manrope", "sans-serif"],
        display: ["Jost", "sans-serif"],
      },
      borderRadius: {
        lg: "0.5rem", // Slightly rounded but boxy
        md: "0.375rem",
        sm: "0.25rem",
      },
      boxShadow: {
        'neo': '4px 4px 0px 0px rgba(0,0,0,1)', // Hard shadow
        'neo-sm': '2px 2px 0px 0px rgba(0,0,0,1)',
        'neo-lg': '6px 6px 0px 0px rgba(0,0,0,1)',
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}


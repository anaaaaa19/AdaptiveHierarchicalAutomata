/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        soc: {
          bg: "#0b1120",
          card: "#151e32",
          border: "#23314d",
          hover: "#1e2c47",
          text: "#f8fafc",
          muted: "#94a3b8",
          accent: "#06b6d4",
          blue: "#3b82f6",
          emerald: "#10b981",
          amber: "#f59e0b",
          rose: "#f43f5e",
          purple: "#8b5cf6",
        }
      }
    },
  },
  plugins: [],
}

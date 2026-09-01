/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        helios: {
          background: '#13131a', // Very dark purple/black
          card: '#1c1c24',       // Darker card background
          cardHover: '#2a2a35',  // Slightly lighter for hover/active
          primary: '#e9c0e9',    // Pinkish/purple text highlight
          purple: '#9333ea',     // Gradient start
          pink: '#db2777',       // Gradient end
          green: '#22c55e',      // Positive indicator
          text: '#f8fafc',       // Main text
          muted: '#9ca3af',      // Muted text
        },
        primary: {
          navy: '#092328',
        },
        secondary: {
          teal: '#12544F',
        },
        positive: {
          DEFAULT: '#8BBB92',
          light: '#e8f3ea',
        },
        attention: {
          DEFAULT: '#F59E0B',
          light: '#fef3c7',
        },
        critical: {
          DEFAULT: '#EF4444',
          light: '#fee2e2',
        },
        background: {
          light: '#F8FAFC',
          dark: '#13131a',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
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
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

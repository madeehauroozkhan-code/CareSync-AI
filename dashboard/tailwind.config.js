/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'system-ui', 'sans-serif'],
      },
      colors: {
        navy: {
          DEFAULT: "#0B3D5C",
          50: '#F2F6F9',
          100: '#E6EDF2',
          200: '#C0D5E1',
          300: '#99BCD1',
          400: '#4D8AA9',
          500: '#0B3D5C',
          600: '#0A3753',
          700: '#072537',
          800: '#051C29',
          900: '#04121C',
        },
        coral: {
          DEFAULT: "#B8442F",
          light: "#FFEAE6",
        },
        teal: {
          DEFAULT: "#1F6F78",
          light: "#E5F5F6",
        },
        amber: {
          DEFAULT: "#D97706",
          light: "#FEF3C7",
        }
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(11, 61, 92, 0.05)',
        'glass-hover': '0 8px 32px 0 rgba(11, 61, 92, 0.12)',
      }
    },
  },
  plugins: [],
};

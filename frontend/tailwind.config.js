/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        rose:  { DEFAULT: '#E8506A', light: '#FDE8EC', mid: '#F5B8C4' },
        sage:  { DEFAULT: '#7BAE8C', light: '#E8F4EC', mid: '#B5D9C0' },
        peach: { DEFAULT: '#F4956A', light: '#FEF0E8' },
        plum:  { DEFAULT: '#6B3D6E', light: '#F0E8F2', mid: '#C4A0C8' },
        cream: '#FBF7F2',
      },
      fontFamily: {
        sans:  ['Nunito', 'sans-serif'],
        serif: ['"DM Serif Display"', 'serif'],
      },
      borderRadius: { xl2: '1.25rem', xl3: '1.5rem' },
      boxShadow: {
        card: '0 4px 24px rgba(107,52,110,0.10)',
        btn:  '0 4px 16px rgba(232,80,106,0.35)',
      },
    },
  },
  plugins: [],
}

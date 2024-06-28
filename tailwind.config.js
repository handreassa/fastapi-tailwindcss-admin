/** @type {import('tailwindcss').Config} */

const DARK_CLASS_NAME = 'dark'
const DARK_COLOR_THEME = 'dark'
const LIGHT_CLASS_NAME = 'light'
const LIGHT_COLOR_THEME = 'light'
const HIDDEN_CLASS_NAME = 'hidden'

module.exports = {
    
}

module.exports = {
  content: ["templates/*.html", "src/*.js", "static/*"],
  // make sure to safelist these classes when using purge
  safelist: [
    'w-64',
    'w-1/2',
    'rounded-l-lg',
    'rounded-r-lg',
    'bg-gray-200',
    'grid-cols-4',
    'grid-cols-7',
    'h-6',
    'leading-6',
    'h-9',
    'leading-9',
    'shadow-lg'
  ],

  // enable dark mode via class strategy
  darkMode: 'class',
  theme: {
    fontFamily: {
      display: ['Roboto Mono', 'Menlo', 'monospace'],
      body: ['Roboto Mono', 'Menlo', 'monospace'],
    },
    colors: {
      primary: {
        50: '#f7fee7',
        100: '#ecfccb',
        200: '#d9f99d',
        300: '#bef264',
        400: '#a3e635',
        500: '#84cc16',
        600: '#65a30d',
        700: '#4d7c0f',
        800: '#3f6212',
        900: '#365314',
      },
      gray: {
        50: '#fafafa',
        100: '#f4f4f5',
        200: '#e4e4e7',
        300: '#d4d4d8',
        400: '#a1a1aa',
        500: '#71717a',
        600: '#52525b',
        700: '#3f3f46',
        800: '#27272a',
        900: '#18181b',
      },
    },
  
  },
  plugins: [
    // include Flowbite as a plugin in your Tailwind CSS project
    require('flowbite/plugin')
  ],
  DARK_CLASS_NAME,
  DARK_COLOR_THEME,
  LIGHT_CLASS_NAME,
  LIGHT_COLOR_THEME,
  HIDDEN_CLASS_NAME,  
}

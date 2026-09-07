import defaultTheme from 'tailwindcss/defaultTheme';
import forms from '@tailwindcss/forms';

/** @type {import('tailwindcss').Config} */
export default {
    content: [
        './vendor/laravel/framework/src/Illuminate/Pagination/resources/views/*.blade.php',
        './storage/framework/views/*.php',
        './resources/views/**/*.blade.php',
    ],

    theme: {
        extend: {
            fontFamily: {
                sans: ['Manrope', ...defaultTheme.fontFamily.sans],
                display: ['"Source Serif 4"', 'Georgia', 'serif'],
            },
            colors: {
                ink: {
                    DEFAULT: '#0f1c24',
                    soft: '#243642',
                },
                mist: '#eef3f6',
                paper: '#f7fafb',
                line: '#d5e0e6',
                brand: {
                    DEFAULT: '#0d7a6f',
                    hover: '#0a635a',
                    soft: '#d8f0ec',
                },
            },
            boxShadow: {
                soft: '0 10px 30px rgba(15, 28, 36, 0.08)',
            },
        },
    },

    plugins: [forms],
};

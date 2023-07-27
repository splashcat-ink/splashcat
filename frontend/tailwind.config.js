/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "../**/templates/**/*.html",
        "../**/*.py",
        "../**/*.js",
    ],
    theme: {
        container: {
            center: true,
            DEFAULT: '1rem',
            sm: '2rem',
            lg: '4rem',
            xl: '5rem',
            '2xl': '6rem',
        },
        extend: {
            fontFamily: {
                splatoon1: ["Splatoon1", "ui-sans-serif", "system-ui", "sans-serif"],
                splatoon2: ["Splatoon2", "ui-sans-serif", "system-ui", "sans-serif"],
            },
            colors: {
                splatoon: {
                    blue: '#603bff',
                    purple: '#a64cf2',
                    yellow: '#eaff3d',
                    green: '#6af7ce',
                    orange: '#ff9750',
                    red: '#ff505e',
                    brown: '#7f413f',

                    battle: {
                        regular: '#19d719',
                        ranked: '#f54910',
                        xmatch: '#0fdb9b',
                        league: '#f02d7d',
                    },
                },
            },
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
    ],
}

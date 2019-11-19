# Vuejs
## Requirements installed

These are the minimum requirements for the project setup:

- [Node.js](http://nodejs.org) - `v8.0+`
- [Git](https://git-scm.com/)

## Getting started

Open your preferred command line tool and run follow some steps below:

1. __`git clone https://github.com/sinthu44/vuejs.git`__.
2. `cd vuejs`.
2. `npm install yarn -g` install yarn.
3. `yarn` automatically to install plugins required for the build script based in `package.json` file.
4. `yarn run dev` to preview and development with url `http://localhost:3000`.
5. `yarn run build` to build final version.


## Project structure

````

vuejs/
├── public
│   ├── static
│   └── index.html
├── src
│   ├── api
│   │   └── api.js
│   ├── components
│   │   └── layout
│   ├── constants
│   ├── containers
│   ├── helpers
│   ├── reducers
│   ├── styles
│   │   └── index.scss
│   ├── App.vue
│   ├── main.js
│   └── router.js
├── .env
├── package.json
└── vue.config.js

````
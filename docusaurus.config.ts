// @ts-check
import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Bridging the gap between the digital brain and the physical body',
  url: 'https://your-vercel-link.vercel.app',
  baseUrl: '/',
  onBrokenLinks: 'ignore',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',

  organizationName: 'panaversity',
  projectName: 'physical-ai-humanoid-textbook',

  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ur'],
    localeConfigs: {
      en: {
        label: 'English',
        direction: 'ltr',
        htmlLang: 'en-US',
        calendar: 'gregory',
        path: 'en',
      },
      ur: {
        label: 'اردو',
        direction: 'rtl', // Urdu is a right-to-left language
        htmlLang: 'ur-PK',
        calendar: 'gregory',
        path: 'ur',
      },
    },
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
        // IMPORTANT: For i18n, always ensure there is a docs plugin instance for each locale
        // If you are using `docusaurus-plugin-content-docs` in advanced mode (not in preset-classic)
        // you would configure instances for each locale.
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'Physical AI & Robotics',
        items: [
          {type: 'docSidebar', sidebarId: 'tutorialSidebar', position: 'left', label: 'Docs'},
          {href: 'https://github.com/', label: 'GitHub', position: 'right'},
          {
            type: 'localeDropdown',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        copyright: `© ${new Date().getFullYear()} Panaversity Physical AI`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
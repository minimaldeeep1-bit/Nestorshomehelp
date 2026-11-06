/** Tailwind build for nestorshomehelp.ca. Run: npm run build (from .claude/tailwind) */
module.exports = {
  content: [
    "../../*.html",
    "../../blog/*.html",
    "../blog/build.py",
    "../blog/posts/*.html",
  ],
  theme: { extend: {} },
  plugins: [],
};

const isProd = process.env.NODE_ENV === "production";

module.exports = {
  typescript: {
    // !! WARN !!
    // Dangerously allow production builds to successfully complete even if
    // your project has type errors.
    // !! WARN !!
    ignoreBuildErrors: true,
  },
  trailingSlash: true, // you can safely remove it, github is smart enough
  basePath: isProd ? "/solsticestreets" : "",
};

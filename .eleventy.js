module.exports = function(eleventyConfig) {
  eleventyConfig.addPassthroughCopy("public");

  // Date filters
  eleventyConfig.addFilter("postDate", (dateObj) => {
    const d = dateObj instanceof Date ? dateObj : new Date(dateObj);
    return d.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
  });

  eleventyConfig.addFilter("date", (dateObj, format) => {
    const d = dateObj instanceof Date ? dateObj : new Date(dateObj || Date.now());
    if (format === "yyyy-MM-dd") {
      return d.toISOString().split('T')[0];
    }
    if (format === "yyyy") {
      return String(d.getFullYear());
    }
    return d.toISOString();
  });

  eleventyConfig.addFilter("categoryLabel", (slug) => {
    const labels = {
      "home-office": "Home Office",
      "luxury-beauty": "Luxury Beauty",
      "kitchen": "Kitchen",
      "fitness": "Fitness",
      "pet-tech": "Pet Tech",
    };
    return labels[slug] || slug;
  });

  eleventyConfig.addFilter("truncate", (str, len) => {
    if (!str) return "";
    if (str.length <= len) return str;
    return str.slice(0, len).replace(/\s\S*$/, "") + "…";
  });

  eleventyConfig.addFilter("slice", (arr, start, end) => {
    if (!arr) return [];
    return end !== undefined ? arr.slice(start, end) : arr.slice(start);
  });

  eleventyConfig.addFilter("stripPathPrefix", (url) => {
    const prefix = "/nickpicks";
    return url && url.startsWith(prefix) ? url.slice(prefix.length) || "/" : (url || "/");
  });

  // Collections
  eleventyConfig.addCollection("articlesByDate", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/articles/*.md")
      .sort((a, b) => b.date - a.date);
  });

  // Global data
  eleventyConfig.addGlobalData("siteUrl", "https://ryonchain.github.io/nickpicks");

  return {
    pathPrefix: "/nickpicks/",
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      data: "_data",
    },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
};

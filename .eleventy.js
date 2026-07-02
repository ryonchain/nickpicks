module.exports = function(eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ "public": "." });

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
      "beauty": "Beauty",
      "kitchen": "Kitchen",
      "fitness": "Fitness",
      "pet-tech": "Pet Tech",
      "smart-home": "Smart Home",
    };
    return labels[slug] || slug;
  });

  eleventyConfig.addFilter("categoryHub", (slug) => {
    const hubs = {
      "home-office": "/home-office/",
      "luxury-beauty": "/beauty/",
      "beauty": "/beauty/",
      "fitness": "/fitness/",
      "health-wellness": "/fitness/",
      "health": "/fitness/",
      "kitchen": "/kitchen/",
      "pet-tech": "/pet-tech/",
    };
    return hubs[slug] || `/categories/${slug}/`;
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

  eleventyConfig.addFilter("whereCategory", (arr, category) => {
    return (arr || []).filter(item => item.data && item.data.category === category);
  });

  eleventyConfig.addFilter("readingTime", (content) => {
    if (!content) return 1;
    const text = content.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
    const words = text.split(" ").filter(w => w.length > 0).length;
    return Math.max(1, Math.ceil(words / 200));
  });

  // Collections
  eleventyConfig.addCollection("articlesByDate", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/articles/*.md")
      .sort((a, b) => b.date - a.date);
  });

  eleventyConfig.addCollection("wellnessArticles", function(collectionApi) {
    const wellnessKeywords = ["ergonomic", "standing-desk", "standing desk", "massage", "treadmill", "sleep"];
    return collectionApi.getFilteredByGlob("src/articles/*.md")
      .filter(article => {
        const category = article.data.category;
        if (category === "fitness") return true;
        if (category === "home-office") {
          const title = (article.data.title || "").toLowerCase();
          const url = (article.url || "").toLowerCase();
          return wellnessKeywords.some(kw => title.includes(kw) || url.includes(kw));
        }
        return false;
      })
      .sort((a, b) => b.date - a.date);
  });

  // Global data
  eleventyConfig.addGlobalData("siteUrl", "https://nickpicks.com");

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

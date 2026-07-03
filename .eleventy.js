const Image = require("@11ty/eleventy-img");

async function imageShortcode(src, alt, sizes) {
  const metadata = await Image(src, {
    widths: [400, 800, 1200],
    formats: ["webp", "jpeg"],
    outputDir: "./_site/images/optimized/",
    urlPath: "/nickpicks/images/optimized/",
  });
  return Image.generateHTML(metadata, {
    alt: alt || "",
    sizes: sizes || "(max-width: 768px) 100vw, 800px",
    loading: "lazy",
    decoding: "async",
  });
}

module.exports = function(eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ "public": "." });

  // Async image shortcode: {% image "src/path.jpg", "alt text" %}
  eleventyConfig.addAsyncShortcode("image", imageShortcode);

  // Add loading="lazy" + decoding="async" to all <img> tags in built HTML.
  // The first <img> on each page keeps loading="eager" for LCP.
  eleventyConfig.addTransform("lazy-images", function(content, outputPath) {
    if (!outputPath || !outputPath.endsWith(".html")) return content;
    let first = true;
    return content.replace(/<img([^>]*)>/gi, (match, attrs) => {
      if (/loading\s*=/i.test(attrs)) return match;
      const loadingVal = first ? "eager" : "lazy";
      first = false;
      if (!/decoding\s*=/i.test(attrs)) {
        return `<img${attrs} loading="${loadingVal}" decoding="async">`;
      }
      return `<img${attrs} loading="${loadingVal}">`;
    });
  });

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
      "gaming": "Gaming",
      "audio-tech": "Audio & Tech",
      "tech": "Tech",
      "outdoor": "Outdoor",
      "travel": "Travel",
      "health": "Health",
      "health-wellness": "Health & Wellness",
      "grooming": "Grooming",
      "baby": "Baby",
      "automotive": "Automotive",
      "home": "Home",
      "home-cleaning": "Home Cleaning",
      "home-improvement": "Home Improvement",
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
      "smart-home": "/categories/smart-home/",
      "gaming": "/categories/gaming/",
      "audio-tech": "/categories/audio-tech/",
      "tech": "/categories/tech/",
      "outdoor": "/categories/outdoor/",
      "travel": "/categories/travel/",
      "grooming": "/categories/grooming/",
      "baby": "/categories/baby/",
      "automotive": "/categories/automotive/",
      "home": "/categories/home/",
      "home-cleaning": "/categories/home-cleaning/",
      "home-improvement": "/categories/home-improvement/",
    };
    return hubs[slug] || null;
  });

  eleventyConfig.addFilter("relatedArticles", (collection, category, currentUrl, count) => {
    count = count || 3;
    if (!collection) return [];

    const adjacentNiches = {
      "home-office": ["gaming", "audio-tech", "tech", "smart-home"],
      "gaming": ["home-office", "audio-tech", "tech"],
      "audio-tech": ["home-office", "gaming", "tech"],
      "tech": ["home-office", "gaming", "audio-tech", "smart-home"],
      "smart-home": ["home-office", "tech", "pet-tech", "home"],
      "kitchen": ["home", "health", "health-wellness"],
      "fitness": ["health", "health-wellness", "outdoor"],
      "health": ["fitness", "health-wellness", "kitchen"],
      "health-wellness": ["fitness", "health", "kitchen"],
      "outdoor": ["fitness", "travel", "automotive"],
      "travel": ["outdoor", "home-office"],
      "luxury-beauty": ["beauty", "grooming", "health-wellness"],
      "beauty": ["luxury-beauty", "grooming", "health-wellness"],
      "grooming": ["beauty", "luxury-beauty", "fitness"],
      "pet-tech": ["smart-home", "home", "outdoor"],
      "home": ["home-office", "smart-home", "home-cleaning", "home-improvement", "kitchen"],
      "home-cleaning": ["home", "smart-home", "home-improvement"],
      "home-improvement": ["home", "outdoor", "home-cleaning"],
      "automotive": ["outdoor", "travel", "tech"],
      "baby": ["smart-home", "home", "health-wellness"],
    };

    const shuffle = arr => {
      const a = arr.slice();
      for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
      }
      return a;
    };

    const isNotSelf = item => item.url !== currentUrl;

    if (!category) {
      return shuffle(collection.filter(isNotSelf)).slice(0, count);
    }

    const primary = shuffle(collection.filter(
      item => item.data && item.data.category === category && isNotSelf(item)
    ));

    if (primary.length >= count) {
      return primary.slice(0, count);
    }

    const neighborCategories = adjacentNiches[category] || [];
    const secondary = shuffle(collection.filter(
      item => item.data && neighborCategories.includes(item.data.category) && isNotSelf(item)
    ));

    const seen = new Set(primary.map(i => i.url));
    const extras = secondary.filter(i => !seen.has(i.url));
    return [...primary, ...extras].slice(0, count);
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

  eleventyConfig.addFilter("urlencode", (str) => encodeURIComponent(str || ""));

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

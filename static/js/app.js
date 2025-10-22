// Global variables
// Removed: const currentLanguage = "en"

// Declare applyTranslations function
// Removed: function applyTranslations(lang) { placeholder for translation logic }

console.log("[v0] Script loaded - Starting immediate initialization...")

function loadStates() {
  console.log("[v0] loadStates() called")

  const states = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Jammu and Kashmir",
  ]

  const stateSelect = document.getElementById("state")
  if (!stateSelect) {
    console.error("[v0] State select element not found!")
    return
  }

  console.log("[v0] State select element found")

  // Clear existing options except the first one
  stateSelect.innerHTML = '<option value="">Select State</option>'

  // Add all state options
  states.forEach((state) => {
    const option = document.createElement("option")
    option.value = state
    option.textContent = state
    stateSelect.appendChild(option)
  })

  console.log("[v0] States loaded successfully:", stateSelect.options.length, "options")
}

function loadSeasons() {
  console.log("[v0] loadSeasons() called")

  const seasons = ["Kharif", "Rabi", "Zaid", "Whole Year", "Summer", "Winter", "Autumn"]

  const seasonSelect = document.getElementById("season")
  if (!seasonSelect) {
    console.error("[v0] Season select element not found!")
    return
  }

  console.log("[v0] Season select element found")

  // Clear existing options except the first one
  seasonSelect.innerHTML = '<option value="">Select Season</option>'

  // Add all season options
  seasons.forEach((season) => {
    const option = document.createElement("option")
    option.value = season
    option.textContent = season
    seasonSelect.appendChild(option)
  })

  console.log("[v0] Seasons loaded successfully:", seasonSelect.options.length, "options")
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("[v0] DOM Content Loaded - Initializing app...")

  try {
    loadStates()
    loadSeasons()
  } catch (e) {
    console.error("[v0] Error loading dropdowns:", e)
  }

  try {
    fetchWeather()
  } catch (e) {
    console.error("[v0] Error fetching weather:", e)
  }

  // Load market prices with local data
  try {
    loadMarketPrices()
  } catch (e) {
    console.error("[v0] Error loading market prices:", e)
  }

  setupEventListeners()

  const savedLanguage = localStorage.getItem("preferredLanguage")
  if (savedLanguage && window.translations && window.translations[savedLanguage]) {
    console.log("[v0] Applying saved language:", savedLanguage)
    if (typeof window.applyTranslations === "function") {
      window.applyTranslations(savedLanguage)
    }
  }

  console.log("[v0] Initialization complete")
})

// Setup event listeners
function setupEventListeners() {
  // Form submission
  const form = document.getElementById("recommendForm")
  if (form) {
    form.addEventListener("submit", handleRecommendation)
    console.log("[v0] Form listener attached")
  }

  document.querySelectorAll("#languageMenu .dropdown-item").forEach((item) => {
    item.addEventListener("click", function (e) {
      e.preventDefault()
      const lang = this.getAttribute("data-lang")
      console.log("[v0] Language menu clicked:", lang)

      if (typeof window.applyTranslations === "function") {
        window.applyTranslations(lang)
      } else {
        console.error("[v0] applyTranslations function not available")
      }
    })
  })

  const weatherCity = document.getElementById("weatherCity")
  if (weatherCity) {
    weatherCity.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        fetchWeather()
      }
    })
  }
}

// Handle recommendation form submission
async function handleRecommendation(e) {
  e.preventDefault()

  const stateEl = document.getElementById("state")
  const seasonEl = document.getElementById("season")

  // Basic validation
  const state = stateEl?.value || ""
  const season = seasonEl?.value || ""
  if (!state) {
    showAlert("Please select a state.", "warning")
    stateEl?.focus()
    return
  }
  if (!season) {
    showAlert("Please select a season.", "warning")
    seasonEl?.focus()
    return
  }

  console.log("[v0] Form submitted for /api/recommend")

  const formData = {
    state,
    season,
    rainfall: (document.getElementById("rainfall")?.value || "").trim(),
    temperature: (document.getElementById("temperature")?.value || "").trim(),
    fertilizer: (document.getElementById("fertilizer")?.value || "").trim(),
    pesticide: (document.getElementById("pesticide")?.value || "").trim(),
    area: (document.getElementById("area")?.value || "").trim(),
  }

  console.log("[v0] Payload:", formData)

  const form = e.target
  const submitBtn = form.querySelector('button[type="submit"]')
  const originalText = submitBtn.innerHTML
  submitBtn.disabled = true
  submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...'

  // Abort after 15s to avoid hanging
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 15000)

  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
      signal: controller.signal,
    })

    const contentType = response.headers.get("content-type") || ""
    const rawText = await response.text()
    const json = contentType.includes("application/json") ? safeParseJson(rawText) : safeParseJson(rawText)

    console.log("[v0] /api/recommend status:", response.status, "json:", json)

    if (!response.ok) {
      const serverMsg =
        (json && (json.error || json.message)) ||
        (rawText && rawText.length < 400 ? rawText : `Server responded with status ${response.status}`)
      showAlert(`Server error: ${serverMsg}`, "danger")
      return
    }

    if (!json || typeof json !== "object") {
      showAlert("Unexpected server response. Please try again.", "danger")
      console.error("[v0] Unexpected response body:", rawText)
      return
    }

    if (json.success) {
      displayRecommendations(json.recommendations || [])
      const results = document.getElementById("resultsSection")
      if (results) {
        results.style.display = "block"
        results.scrollIntoView({ behavior: "smooth" })
      }
      showAlert("Recommendations loaded successfully!", "success")
    } else {
      showAlert("Error getting recommendations: " + (json.error || "Unknown error"), "danger")
    }
  } catch (error) {
    if (error.name === "AbortError") {
      showAlert("Request timed out. Please try again.", "danger")
    } else {
      console.error("[v0] Network/parse error:", error)
      showAlert("Could not reach the server. Check if Flask is running and try again.", "danger")
    }
  } finally {
    clearTimeout(timeout)
    submitBtn.disabled = false
    submitBtn.innerHTML = originalText
  }
}

// Display recommendations
function displayRecommendations(recommendations) {
  const container = document.getElementById("recommendationsContainer")
  container.innerHTML = ""

  if (recommendations.length === 0) {
    container.innerHTML =
      '<div class="col-12"><p class="text-center text-muted">No recommendations found for the given conditions.</p></div>'
    return
  }

  recommendations.forEach((rec, index) => {
    const card = createEnhancedRecommendationCard(rec, index)
    container.appendChild(card)
  })
}

// Create recommendation card
function createEnhancedRecommendationCard(rec, index) {
  const col = document.createElement("div")
  col.className = "col-12"

  // Calculate compatibility score (based on confidence)
  const compatibilityScore = Math.round(rec.confidence)

  // Determine match level
  let matchLevel = "beginner"
  if (compatibilityScore >= 70) matchLevel = "expert"
  else if (compatibilityScore >= 50) matchLevel = "intermediate"

  // Get match level color
  const matchColor = compatibilityScore >= 70 ? "success" : compatibilityScore >= 50 ? "warning" : "secondary"

  // Parse pros and cons
 const prosArray = Array.isArray(rec.pros)
  ? rec.pros
  : typeof rec.pros === "string"
  ? rec.pros.split(".").filter((p) => p.trim())
  : []

const consArray = Array.isArray(rec.cons)
  ? rec.cons
  : typeof rec.cons === "string"
  ? rec.cons.split(".").filter((c) => c.trim())
  : []


  // Generate expert tips based on crop
  const expertTips = generateExpertTips(rec.crop, rec.growing_season)

  // Generate considerations based on conditions
  const considerations = generateConsiderations(rec)

  const category = getCropCategory(rec.crop)

  col.innerHTML = `
        <div class="card crop-detail-card shadow-sm mb-4">
            <div class="card-body p-4"> 
                <div class="d-flex justify-content-between align-items-start mb-4">
                    <div>
                        <h4 class="mb-2 d-flex align-items-center">
    <img src="/static/images/crops/${rec.crop.toLowerCase()}.jpg" 
         alt="${rec.crop}" 
         class="me-2 rounded" 
         style="width: 100px; height: 100px; object-fit: cover; border: 2px solid #dee2e6;">
    <span>${rec.crop}</span>
    <span class="badge bg-light text-dark ms-2">${category}</span>
</h4>

                        <p class="text-muted mb-0">
                            <i class="bi bi-graph-up"></i> Expected Yield: <strong>${rec.avg_yield || "2.5-4.0"} tons/hectare</strong>
                            <span class="ms-3"><i class="bi bi-calendar3"></i> Growth Period: <strong>${getGrowthPeriod(rec.crop)}</strong></span>
                        </p>
                    </div>
                    <div class="text-end">
                        <span class="badge bg-${matchColor} fs-6 mb-2">${compatibilityScore}% Match</span>
                        <br>
                        <span class="badge bg-secondary">${matchLevel}</span>
                    </div>
                </div>
                <div class="mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="mb-0">Compatibility Score</h6>
                        <span class="text-success fw-bold">${compatibilityScore}%</span>
                    </div>
                    <div class="progress" style="height: 12px;">
                        <div class="progress-bar bg-success" role="progressbar" style="width: ${compatibilityScore}%" 
                             aria-valuenow="${compatibilityScore}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                </div>
                <div class="mb-4">
                    <h6 class="mb-3">
                        <i class="bi bi-check-circle text-success"></i> Why This Crop Works For You:
                    </h6>
                    <div class="ps-3">
                        ${prosArray
                          .slice(0, 3)
                          .map(
                            (pro) => `<p class="mb-2"><i class="bi bi-check text-success me-2"></i>${pro.trim()}</p>`,
                          )
                          .join("")}
                        ${prosArray.length === 0 ? `<p class="mb-2"><i class="bi bi-check text-success me-2"></i>Optimal soil type (${rec.soil_type || "loam"})</p><p class="mb-2"><i class="bi bi-check text-success me-2"></i>Good market demand (${rec.market_demand || "High"})</p><p class="mb-2"><i class="bi bi-check text-success me-2"></i>Suitable for ${rec.growing_season || "current season"}</p>` : ""}
                    </div>
                </div>
                ${
                  considerations.length > 0
                    ? `
                <div class="mb-4">
                    <h6 class="mb-3">
                        <i class="bi bi-exclamation-triangle text-warning"></i> Considerations:
                    </h6>
                    <div class="ps-3">
                        ${considerations.map((con) => `<p class="mb-2 text-muted"><i class="bi bi-exclamation-triangle text-warning me-2"></i>${con}</p>`).join("")}
                    </div>
                </div>
                `
                    : ""
                } 
                <div class="mb-4">
                    <h6 class="mb-3">Expert Growing Tips:</h6>
                    <ul class="ps-3">
                        ${expertTips.map((tip) => `<li class="mb-2">${tip}</li>`).join("")}
                    </ul>
                </div>

                 Additional Info 
                <div class="row g-3 mt-3 pt-3 border-top">
                    <div class="col-md-4 text-center">
                        <small class="text-muted d-block mb-1">Season</small>
                        <strong>${rec.growing_season || "All seasons"}</strong>
                    </div>
                    <div class="col-md-4 text-center">
                        <small class="text-muted d-block mb-1">Water Need</small>
                        <strong>${getWaterNeed(rec.crop)}</strong>
                    </div>
                    <div class="col-md-4 text-center">
                        <small class="text-muted d-block mb-1">Profitability</small>
                        <strong class="text-success">${rec.market_demand || "High"}</strong>
                    </div>
                </div>

                 Market Info 
                <div class="mt-3 p-3 bg-light rounded">
                    <div class="row align-items-center">
                        <div class="col-md-6">
                            <small class="text-muted">Current Market Price</small>
                            <h5 class="mb-0 text-success">₹${rec.market_price || "2500"}/quintal</h5>
                        </div>
                        <div class="col-md-6 text-md-end">
                            <span class="badge ${rec.price_trend === "rising" ? "bg-success" : rec.price_trend === "falling" ? "bg-danger" : "bg-secondary"}">
                                <i class="bi ${rec.price_trend === "rising" ? "bi-arrow-up" : rec.price_trend === "falling" ? "bi-arrow-down" : "bi-dash"}"></i>
                                ${rec.price_trend || "stable"} ${rec.price_change ? `(${rec.price_change}%)` : ""}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `

  return col
}

function generateExpertTips(crop, season) {
  const tips = {
    Wheat: [
      "Plant when soil temperature is consistently above 4°C",
      "Ensure good drainage to prevent waterlogging",
      "Monitor for rust and powdery mildew diseases",
      "Apply nitrogen fertilizer in split doses",
    ],
    Rice: [
      "Maintain 2-3 inches of standing water during growing season",
      "Transplant seedlings at 21-25 days old",
      "Monitor for blast disease and stem borers",
      "Apply phosphorus at planting time",
    ],
    Cotton: [
      "Plant when soil temperature is consistently above 18°C",
      "Requires long frost-free growing season",
      "Monitor for bollworm and other pests",
      "Harvest when bolls are fully open",
    ],
    Maize: [
      "Plant after soil temperature reaches 10°C",
      "Tolerates drought once established",
      "Faces east in morning, follows sun during day",
      "Harvest when back of head turns brown",
    ],
    Sugarcane: [
      "Requires consistent moisture throughout growing season",
      "Plant in well-drained, fertile soil",
      "Monitor for red rot and smut diseases",
      "Harvest at 10-12 months for optimal sugar content",
    ],
    Sunflower: [
      "Plant when soil temperature is consistently above 8°C",
      "Requires full sun exposure for best yields",
      "Monitor for rust and downy mildew",
      "Harvest when back of head turns yellow-brown",
    ],
  }

  return (
    tips[crop] || [
      "Prepare soil with adequate organic matter",
      "Follow recommended spacing for optimal growth",
      "Monitor regularly for pests and diseases",
      "Harvest at the right maturity stage for best quality",
    ]
  )
}

function generateConsiderations(rec) {
  const considerations = []

  // Add considerations based on cons
 if (rec.cons) {
    const consArray = Array.isArray(rec.cons)
        ? rec.cons
        : typeof rec.cons === "string"
        ? rec.cons.split(".").filter((c) => c.trim())
        : []

 }
  // Add generic considerations if none exist
  if (considerations.length === 0) {
    considerations.push("Monitor weather conditions regularly")
    considerations.push("Ensure proper irrigation management")
    considerations.push("Follow integrated pest management practices")
  }

  return considerations
}

function getCropCategory(crop) {
  const categories = {
    Wheat: "cereal",
    Rice: "cereal",
    Maize: "cereal",
    Barley: "cereal",
    Cotton: "fiber",
    Jute: "fiber",
    Sugarcane: "cash crop",
    Sunflower: "oilseed",
    Groundnut: "oilseed",
    Soybean: "oilseed",
    Potato: "vegetable",
    Tomato: "vegetable",
    Onion: "vegetable",
  }

  return categories[crop] || "crop"
}

function getGrowthPeriod(crop) {
  const periods = {
    Wheat: "120-150 days",
    Rice: "120-150 days",
    Maize: "90-120 days",
    Cotton: "180-200 days",
    Sugarcane: "10-12 months",
    Sunflower: "90-120 days",
    Potato: "90-120 days",
    Tomato: "60-90 days",
    Onion: "100-120 days",
  }

  return periods[crop] || "90-150 days"
}

function getWaterNeed(crop) {
  const waterNeeds = {
    Rice: "High",
    Sugarcane: "High",
    Cotton: "Medium",
    Wheat: "Medium",
    Maize: "Medium",
    Sunflower: "Low",
    Sorghum: "Low",
  }

  return waterNeeds[crop] || "Medium"
}

async function fetchWeather() {
  const city = document.getElementById("weatherCity").value || "Delhi"
  const weatherData = document.getElementById("weatherData")

  console.log("[v0] Fetching weather for:", city)

  weatherData.innerHTML =
    '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>'

  try {
    const response = await fetch(`/api/weather/${encodeURIComponent(city)}`)
    const data = await response.json()

    console.log("[v0] Weather data:", data)

    if (data.success) {
      weatherData.innerHTML = `
                <div class="text-center">
                    <i class="bi bi-geo-alt-fill text-primary"></i>
                    <h6 class="mb-0">${data.city}</h6>
                </div>
                <div class="text-center">
                    <div class="weather-icon">
                        <i class="bi bi-cloud-sun-fill"></i>
                    </div>
                    <h3 class="mb-0">${data.temperature}°C</h3>
                    <small class="text-muted">${data.description}</small>
                </div>
                <div class="text-center">
                    <p class="mb-1"><i class="bi bi-droplet-fill text-info"></i> ${data.humidity}%</p>
                    <small class="text-muted">Humidity</small>
                </div>
                <div class="text-center">
                    <p class="mb-1"><i class="bi bi-wind text-primary"></i> ${data.wind_speed} m/s</p>
                    <small class="text-muted">Wind Speed</small>
                </div>
            `

      // Auto-fill temperature in form
      const tempInput = document.getElementById("temperature")
      if (tempInput && !tempInput.value) {
        tempInput.value = Math.round(data.temperature)
      }
    } else {
      weatherData.innerHTML = '<p class="text-danger">Unable to fetch weather data</p>'
    }
  } catch (error) {
    console.error("[v0] Weather error:", error)
    weatherData.innerHTML = '<p class="text-danger">Error loading weather</p>'
  }
}

async function loadMarketPrices() {
  console.log("[v0] loadMarketPrices() called")

  const fallbackPrices = {
    Wheat: { price: "2500", unit: "per quintal", trend: "rising" },
    Rice: { price: "3200", unit: "per quintal", trend: "stable" },
    Cotton: { price: "6800", unit: "per quintal", trend: "rising" },
    Maize: { price: "1900", unit: "per quintal", trend: "falling" },
    Sugarcane: { price: "3500", unit: "per ton", trend: "stable" },
    Soybean: { price: "4200", unit: "per quintal", trend: "rising" },
    Groundnut: { price: "5500", unit: "per quintal", trend: "rising" },
    Sunflower: { price: "6200", unit: "per quintal", trend: "stable" },
  }

  // Display local data immediately
  displayMarketPrices(fallbackPrices)
}

function displayMarketPrices(prices) {
  console.log("[v0] displayMarketPrices() called with", Object.keys(prices).length, "prices")

  const container = document.getElementById("marketPricesContainer")

  if (!container) {
    console.error("[v0] Market prices container not found!")
    return
  }

  // Clear container
  container.innerHTML = ""
  console.log("[v0] Container cleared")

  // Create price cards
  let cardsCreated = 0
  Object.entries(prices).forEach(([crop, data]) => {
    const trendIcon =
      data.trend === "rising"
        ? "bi-arrow-up-circle-fill text-success"
        : data.trend === "falling"
          ? "bi-arrow-down-circle-fill text-danger"
          : "bi-dash-circle-fill text-secondary"

    const col = document.createElement("div")
    col.className = "col-md-4 col-lg-3 mb-3"
    col.innerHTML = `
            <div class="card h-100 shadow-sm">
                <div class="card-body text-center">
                    <h6 class="card-title mb-3">${crop}</h6>
                    <h4 class="text-success mb-2">₹${data.price}</h4>
                    <p class="mb-2 small text-muted">${data.unit}</p>
                    <p class="mb-0">
                        <i class="bi ${trendIcon}"></i> 
                        <span class="text-capitalize">${data.trend}</span>
                    </p>
                </div>
            </div>
        `
    container.appendChild(col)
    cardsCreated++
  })

  console.log("[v0] Market prices displayed:", cardsCreated, "cards created")
}

// Show alert
function showAlert(message, type = "info") {
  const alertDiv = document.createElement("div")
  alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`
  alertDiv.style.zIndex = "9999"
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `
  document.body.appendChild(alertDiv)

  setTimeout(() => {
    alertDiv.remove()
  }, 5000)
}

// Scroll to recommend section
function scrollToRecommend() {
  document.getElementById("recommend").scrollIntoView({ behavior: "smooth" })
}

window.fetchWeather = fetchWeather
window.showAlert = showAlert
window.loadStates = loadStates
window.loadSeasons = loadSeasons

// Safe JSON parser to avoid crashes when backend returns HTML on errors
function safeParseJson(text) {
  try {
    return JSON.parse(text)
  } catch {
    return null
  }
}

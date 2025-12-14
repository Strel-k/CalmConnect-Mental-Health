// Client-side rate limiting solution for CalmConnect API calls
// This file provides rate limiting, retry logic, and exponential backoff
// to prevent 403 Forbidden errors from server-side rate limiting

// Install bottleneck: npm install bottleneck

const Bottleneck = require('bottleneck');

// Rate limiter configuration
// Adjust these values based on your API limits
const rateLimiter = new Bottleneck({
  maxConcurrent: 1, // Only 1 concurrent request
  minTime: 200, // Minimum 200ms between requests
  reservoir: 45, // 45 requests per minute (leaving buffer below 50/min limit)
  reservoirRefreshAmount: 45,
  reservoirRefreshInterval: 60 * 1000, // Refresh every minute
  trackDoneStatus: true
});

// Retry configuration
const MAX_RETRIES = 3;
const BASE_DELAY = 1000; // 1 second base delay
const MAX_DELAY = 30000; // 30 seconds max delay

/**
 * Sleep utility function
 * @param {number} ms - Milliseconds to sleep
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Calculate exponential backoff delay
 * @param {number} attempt - Current attempt number (0-based)
 * @returns {number} Delay in milliseconds
 */
function calculateBackoffDelay(attempt) {
  const delay = BASE_DELAY * Math.pow(2, attempt);
  // Add jitter to prevent thundering herd
  const jitter = Math.random() * 0.1 * delay;
  return Math.min(delay + jitter, MAX_DELAY);
}

/**
 * Check if error is rate limit related
 * @param {Response} response - Fetch response object
 * @returns {boolean} True if rate limited
 */
function isRateLimited(response) {
  return response.status === 403 || response.status === 429;
}

/**
 * Make API request with rate limiting and retry logic
 * @param {string} url - API endpoint URL
 * @param {object} options - Fetch options
 * @returns {Promise<Response>} Fetch response
 */
async function makeRateLimitedRequest(url, options = {}) {
  return rateLimiter.schedule(async () => {
    let lastError;

    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      try {
        console.log(`Making request to ${url} (attempt ${attempt + 1}/${MAX_RETRIES + 1})`);

        const response = await fetch(url, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers
          }
        });

        // If successful or not a rate limit error, return response
        if (!isRateLimited(response)) {
          return response;
        }

        // Rate limited - check if we should retry
        if (attempt < MAX_RETRIES) {
          const delay = calculateBackoffDelay(attempt);
          console.warn(`Rate limited (status: ${response.status}). Retrying in ${delay}ms...`);
          await sleep(delay);
          continue;
        } else {
          // Max retries reached
          console.error(`Max retries reached for ${url}. Final status: ${response.status}`);
          return response;
        }

      } catch (error) {
        lastError = error;
        console.error(`Request failed (attempt ${attempt + 1}):`, error);

        // For network errors, retry if not max attempts
        if (attempt < MAX_RETRIES) {
          const delay = calculateBackoffDelay(attempt);
          console.warn(`Network error. Retrying in ${delay}ms...`);
          await sleep(delay);
          continue;
        }
      }
    }

    // If we get here, all retries failed
    throw lastError || new Error('Max retries exceeded');
  });
}

/**
 * Generate personalized tips with rate limiting and retry logic
 * @param {object} data - Request data
 * @returns {Promise<object>} Response data
 */
async function generatePersonalizedTips(data) {
  try {
    const response = await makeRateLimitedRequest('/api/generate-tips/', {
      method: 'POST',
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.message || 'Unknown error'}`);
    }

    const result = await response.json();
    console.log('Personalized tips generated successfully');
    return result;

  } catch (error) {
    console.error('Error fetching enhanced AI tips:', error);
    throw error;
  }
}

/**
 * Fetch AI feedback with rate limiting and retry logic
 * @param {object} data - Request data
 * @returns {Promise<object>} Response data
 */
async function fetchAIFeedback(data) {
  try {
    const response = await makeRateLimitedRequest('/api/ai-feedback/', {
      method: 'POST',
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.message || 'Unknown error'}`);
    }

    const result = await response.json();
    console.log('AI feedback fetched successfully');
    return result;

  } catch (error) {
    console.error('Error fetching AI feedback:', error);
    throw error;
  }
}

// Alternative implementation without Bottleneck (manual throttling)
/**
 * Manual rate limiter class (alternative to Bottleneck)
 */
class ManualRateLimiter {
  constructor(requestsPerMinute = 45, minInterval = 200) {
    this.requestsPerMinute = requestsPerMinute;
    this.minInterval = minInterval;
    this.requests = [];
    this.lastRequestTime = 0;
  }

  async throttle() {
    const now = Date.now();

    // Remove old requests outside the time window
    const oneMinuteAgo = now - 60000;
    this.requests = this.requests.filter(time => time > oneMinuteAgo);

    // Check if we're at the limit
    if (this.requests.length >= this.requestsPerMinute) {
      const oldestRequest = Math.min(...this.requests);
      const waitTime = 60000 - (now - oldestRequest);
      if (waitTime > 0) {
        console.log(`Rate limit reached. Waiting ${waitTime}ms...`);
        await sleep(waitTime);
      }
    }

    // Ensure minimum interval between requests
    const timeSinceLastRequest = now - this.lastRequestTime;
    if (timeSinceLastRequest < this.minInterval) {
      const waitTime = this.minInterval - timeSinceLastRequest;
      await sleep(waitTime);
    }

    this.requests.push(now);
    this.lastRequestTime = Date.now();
  }
}

// Manual rate limiter instance
const manualLimiter = new ManualRateLimiter();

/**
 * Make request with manual rate limiting (alternative to Bottleneck)
 * @param {string} url - API endpoint URL
 * @param {object} options - Fetch options
 * @returns {Promise<Response>} Fetch response
 */
async function makeManualRateLimitedRequest(url, options = {}) {
  await manualLimiter.throttle();

  let lastError;

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      console.log(`Making request to ${url} (attempt ${attempt + 1}/${MAX_RETRIES + 1})`);

      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      });

      if (!isRateLimited(response)) {
        return response;
      }

      if (attempt < MAX_RETRIES) {
        const delay = calculateBackoffDelay(attempt);
        console.warn(`Rate limited (status: ${response.status}). Retrying in ${delay}ms...`);
        await sleep(delay);
        continue;
      } else {
        console.error(`Max retries reached for ${url}. Final status: ${response.status}`);
        return response;
      }

    } catch (error) {
      lastError = error;
      console.error(`Request failed (attempt ${attempt + 1}):`, error);

      if (attempt < MAX_RETRIES) {
        const delay = calculateBackoffDelay(attempt);
        console.warn(`Network error. Retrying in ${delay}ms...`);
        await sleep(delay);
        continue;
      }
    }
  }

  throw lastError || new Error('Max retries exceeded');
}

// Export functions for use in your application
module.exports = {
  generatePersonalizedTips,
  fetchAIFeedback,
  makeRateLimitedRequest,
  makeManualRateLimitedRequest,
  ManualRateLimiter
};

// Usage examples:
/*
// In your existing code, replace direct fetch calls with:

// Instead of:
const tipsResponse = await fetch('/api/generate-tips/', {
  method: 'POST',
  body: JSON.stringify(data)
});

// Use:
const tipsResult = await generatePersonalizedTips(data);

// Instead of:
const feedbackResponse = await fetch('/api/ai-feedback/', {
  method: 'POST',
  body: JSON.stringify(data)
});

// Use:
const feedbackResult = await fetchAIFeedback(data);
*/
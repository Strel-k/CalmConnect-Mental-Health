// FRONTEND JAVASCRIPT WITH RATE LIMITING IMPLEMENTED
// Replace your existing frontend JavaScript with this file
// Install bottleneck first: npm install bottleneck

const Bottleneck = require('bottleneck');

// Rate limiter configuration - stays under 50 requests/minute server limit
const rateLimiter = new Bottleneck({
  maxConcurrent: 1,           // Only 1 concurrent request
  minTime: 200,              // Minimum 200ms between requests
  reservoir: 45,             // 45 requests per minute (safe buffer)
  reservoirRefreshAmount: 45,
  reservoirRefreshInterval: 60 * 1000, // Refresh every minute
});

// Utility functions
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function calculateBackoffDelay(attempt) {
  const delay = 1000 * Math.pow(2, attempt); // Exponential backoff
  const jitter = Math.random() * 0.1 * delay; // Add 10% jitter
  return Math.min(delay + jitter, 30000); // Cap at 30 seconds
}

function isRateLimited(response) {
  return response.status === 403 || response.status === 429;
}

// Rate-limited request function with retry logic
async function makeRateLimitedRequest(url, options = {}) {
  return rateLimiter.schedule(async () => {
    let lastError;

    for (let attempt = 0; attempt <= 3; attempt++) {
      try {
        console.log(`Making request to ${url} (attempt ${attempt + 1}/4)`);

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

        if (attempt < 3) {
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

        if (attempt < 3) {
          const delay = calculateBackoffDelay(attempt);
          console.warn(`Network error. Retrying in ${delay}ms...`);
          await sleep(delay);
          continue;
        }
      }
    }

    throw lastError || new Error('Max retries exceeded');
  });
}

// RATE-LIMITED VERSION OF generatePersonalizedTips
async function generatePersonalizedTips(data) {
  try {
    const response = await makeRateLimitedRequest('https://calm-connect.up.railway.app/api/generate-tips/', {
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

// RATE-LIMITED VERSION OF fetchAIFeedback
async function fetchAIFeedback(data) {
  try {
    const response = await makeRateLimitedRequest('https://calm-connect.up.railway.app/api/ai-feedback/', {
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

// MANUAL RATE LIMITING FALLBACK (uncomment if bottleneck fails)
/*
class ManualRateLimiter {
  constructor(requestsPerMinute = 45, minInterval = 200) {
    this.requestsPerMinute = requestsPerMinute;
    this.minInterval = minInterval;
    this.requests = [];
    this.lastRequestTime = 0;
  }

  async throttle() {
    const now = Date.now();
    const oneMinuteAgo = now - 60000;
    this.requests = this.requests.filter(time => time > oneMinuteAgo);

    if (this.requests.length >= this.requestsPerMinute) {
      const oldestRequest = Math.min(...this.requests);
      const waitTime = 60000 - (now - oldestRequest);
      if (waitTime > 0) {
        console.log(`Rate limit reached. Waiting ${waitTime}ms...`);
        await sleep(waitTime);
      }
    }

    const timeSinceLastRequest = now - this.lastRequestTime;
    if (timeSinceLastRequest < this.minInterval) {
      const waitTime = this.minInterval - timeSinceLastRequest;
      await sleep(waitTime);
    }

    this.requests.push(now);
    this.lastRequestTime = Date.now();
  }
}

const manualLimiter = new ManualRateLimiter();

async function makeManualRateLimitedRequest(url, options = {}) {
  await manualLimiter.throttle();

  let lastError;

  for (let attempt = 0; attempt <= 3; attempt++) {
    try {
      console.log(`Making request to ${url} (attempt ${attempt + 1}/4)`);

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

      if (attempt < 3) {
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

      if (attempt < 3) {
        const delay = calculateBackoffDelay(attempt);
        console.warn(`Network error. Retrying in ${delay}ms...`);
        await sleep(delay);
        continue;
      }
    }
  }

  throw lastError || new Error('Max retries exceeded');
}

// Replace makeRateLimitedRequest with makeManualRateLimitedRequest in the functions above
*/

// Export functions if using modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    generatePersonalizedTips,
    fetchAIFeedback,
    makeRateLimitedRequest
  };
}
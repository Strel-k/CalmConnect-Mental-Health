// Rate Limiting Client-Side Implementation for CalmConnect
// This file provides examples of implementing rate limiting, throttling, and retry logic
// for the generatePersonalizedTips and fetchAIFeedback functions

// Option 1: Using Bottleneck library (recommended for complex scenarios)
// Install with: npm install bottleneck

class APIRateLimiter {
    constructor() {
        // Initialize bottleneck limiter
        this.limiter = new Bottleneck({
            minTime: 200, // Minimum 200ms between requests
            maxConcurrent: 1, // Only 1 concurrent request
            reservoir: 45, // 45 requests
            reservoirRefreshAmount: 45,
            reservoirRefreshInterval: 60 * 1000, // Refreshes every minute
        });

        // Configure retry logic
        this.limiter.on("failed", async (error, jobInfo) => {
            const { retryCount } = jobInfo;
            console.warn(`Request failed (attempt ${retryCount + 1}):`, error);

            if (error.status === 429 || error.status === 403) {
                // Rate limited - exponential backoff
                const delay = Math.min(1000 * Math.pow(2, retryCount), 30000); // Max 30 seconds
                console.log(`Rate limited. Retrying in ${delay}ms...`);
                return delay;
            }

            // Don't retry for other errors
            return false;
        });

        this.limiter.on("retry", (error, jobInfo) => {
            console.log(`Retrying request after failure...`);
        });
    }

    async makeRequest(url, options = {}) {
        return this.limiter.schedule(async () => {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                body: JSON.stringify(options.body)
            });

            if (!response.ok) {
                const error = new Error(`HTTP error! status: ${response.status}`);
                error.status = response.status;
                throw error;
            }

            return response.json();
        });
    }
}

// Option 2: Manual throttling implementation (no external dependencies)

class ManualRateLimiter {
    constructor() {
        this.requests = [];
        this.maxRequestsPerMinute = 45;
        this.minInterval = 200; // Minimum 200ms between requests
        this.lastRequestTime = 0;
    }

    async throttle() {
        const now = Date.now();

        // Clean old requests (older than 1 minute)
        this.requests = this.requests.filter(time => now - time < 60000);

        // Check if we're within rate limits
        if (this.requests.length >= this.maxRequestsPerMinute) {
            const oldestRequest = Math.min(...this.requests);
            const waitTime = 60000 - (now - oldestRequest);
            if (waitTime > 0) {
                console.log(`Rate limit reached. Waiting ${waitTime}ms...`);
                await this.delay(waitTime);
            }
        }

        // Ensure minimum interval between requests
        const timeSinceLastRequest = now - this.lastRequestTime;
        if (timeSinceLastRequest < this.minInterval) {
            const waitTime = this.minInterval - timeSinceLastRequest;
            await this.delay(waitTime);
        }

        this.requests.push(now);
        this.lastRequestTime = Date.now();
    }

    async delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async makeRequest(url, options = {}, retryCount = 0) {
        await this.throttle();

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                body: JSON.stringify(options.body)
            });

            if (!response.ok) {
                if ((response.status === 429 || response.status === 403) && retryCount < 3) {
                    // Rate limited - exponential backoff
                    const delay = Math.min(1000 * Math.pow(2, retryCount), 30000);
                    console.log(`Rate limited. Retrying in ${delay}ms (attempt ${retryCount + 1}/3)...`);
                    await this.delay(delay);
                    return this.makeRequest(url, options, retryCount + 1);
                }

                const error = new Error(`HTTP error! status: ${response.status}`);
                error.status = response.status;
                throw error;
            }

            return response.json();
        } catch (error) {
            if (retryCount < 3 && (error.status === 429 || error.status === 403)) {
                const delay = Math.min(1000 * Math.pow(2, retryCount), 30000);
                console.log(`Request failed. Retrying in ${delay}ms (attempt ${retryCount + 1}/3)...`);
                await this.delay(delay);
                return this.makeRequest(url, options, retryCount + 1);
            }
            throw error;
        }
    }
}

// Global rate limiter instances
const bottleneckLimiter = new APIRateLimiter();
const manualLimiter = new ManualRateLimiter();

// Updated generatePersonalizedTips function with rate limiting
async function generatePersonalizedTips(depression, anxiety, stress, depressionSeverity, anxietySeverity, stressSeverity, answers) {
    try {
        console.log('Generating personalized tips...');

        const response = await manualLimiter.makeRequest('https://calm-connect.up.railway.app/api/generate-tips/', {
            body: {
                depression,
                anxiety,
                stress,
                depression_severity: depressionSeverity,
                anxiety_severity: anxietySeverity,
                stress_severity: stressSeverity,
                answers
            }
        });

        console.log('Tips generated successfully:', response);
        return response;

    } catch (error) {
        console.error('Error fetching enhanced AI tips:', error);

        // Show user-friendly error message
        if (error.status === 429) {
            showErrorMessage('Rate limit exceeded. Please wait a moment before trying again.');
        } else if (error.status === 403) {
            showErrorMessage('Access denied. Please check your authentication.');
        } else {
            showErrorMessage('Failed to generate tips. Please try again later.');
        }

        throw error;
    }
}

// Updated fetchAIFeedback function with rate limiting
async function fetchAIFeedback(depression, anxiety, stress, depressionSeverity, anxietySeverity, stressSeverity, answers) {
    try {
        console.log('Fetching AI feedback...');

        const response = await manualLimiter.makeRequest('https://calm-connect.up.railway.app/api/ai-feedback/', {
            body: {
                depression,
                anxiety,
                stress,
                depression_severity: depressionSeverity,
                anxiety_severity: anxietySeverity,
                stress_severity: stressSeverity,
                answers
            }
        });

        console.log('AI feedback received:', response);
        return response;

    } catch (error) {
        console.error('Error fetching AI feedback:', error);

        // Show user-friendly error message
        if (error.status === 429) {
            showErrorMessage('Rate limit exceeded. Please wait a moment before trying again.');
        } else if (error.status === 403) {
            showErrorMessage('Access denied. Please check your authentication.');
        } else {
            showErrorMessage('Failed to get AI feedback. Please try again later.');
        }

        throw error;
    }
}

// Alternative implementation using Bottleneck (if you prefer the library approach)
// Uncomment the lines below and comment out the manualLimiter calls above

/*
async function generatePersonalizedTips(depression, anxiety, stress, depressionSeverity, anxietySeverity, stressSeverity, answers) {
    try {
        console.log('Generating personalized tips...');

        const response = await bottleneckLimiter.makeRequest('https://calm-connect.up.railway.app/api/generate-tips/', {
            body: {
                depression,
                anxiety,
                stress,
                depression_severity: depressionSeverity,
                anxiety_severity: anxietySeverity,
                stress_severity: stressSeverity,
                answers
            }
        });

        console.log('Tips generated successfully:', response);
        return response;

    } catch (error) {
        console.error('Error fetching enhanced AI tips:', error);
        showErrorMessage('Failed to generate tips. Please try again later.');
        throw error;
    }
}

async function fetchAIFeedback(depression, anxiety, stress, depressionSeverity, anxietySeverity, stressSeverity, answers) {
    try {
        console.log('Fetching AI feedback...');

        const response = await bottleneckLimiter.makeRequest('https://calm-connect.up.railway.app/api/ai-feedback/', {
            body: {
                depression,
                anxiety,
                stress,
                depression_severity: depressionSeverity,
                anxiety_severity: anxietySeverity,
                stress_severity: stressSeverity,
                answers
            }
        });

        console.log('AI feedback received:', response);
        return response;

    } catch (error) {
        console.error('Error fetching AI feedback:', error);
        showErrorMessage('Failed to get AI feedback. Please try again later.');
        throw error;
    }
}
*/

// Helper function to show error messages (implement according to your UI framework)
function showErrorMessage(message) {
    // Example implementation - adjust based on your UI
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ff4444;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        z-index: 1000;
        max-width: 300px;
    `;

    document.body.appendChild(errorDiv);

    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}

// Export for use in other modules (if using modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        APIRateLimiter,
        ManualRateLimiter,
        generatePersonalizedTips,
        fetchAIFeedback
    };
}
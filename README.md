# Website Grader

A comprehensive tool for analyzing and scoring websites based on various technical and design aspects. This tool helps identify potential leads for web development and design services by evaluating websites across multiple categories.

## Features

### 1. SSL Certificate Analysis (10% of total score)
- Checks HTTPS implementation
- Validates SSL certificate
- Evaluates security configuration

### 2. Mobile-Friendliness (15% of total score)
- Responsive design detection
- Mobile viewport configuration
- Touch element spacing
- Font size and readability

### 3. Page Speed (15% of total score)
- Initial load time measurement
- Resource optimization
- Performance metrics:
  - < 1s: Excellent (100%)
  - < 2s: Good (75%)
  - < 3s: Average (50%)
  - < 5s: Poor (25%)
  - > 5s: Very Poor (0%)

### 4. Technology Stack (25% of total score)
Modern Framework Detection:
- Next.js (+5 points)
- React (+4 points)
- Vue 3 (+4 points)
- Nuxt.js (+5 points)
- Angular (+4 points)
- Svelte (+4 points)
- Remix (+5 points)
- Gatsby (+4 points)

*Note: Mixing modern and legacy technologies results in a -2 point penalty*

### 5. UI Quality (10% of total score)
- Design consistency
- Color scheme
- Typography
- Layout structure
- Interactive elements

### 6. SEO Optimization (5% of total score)
- Meta tags
- Heading structure
- Image alt texts
- URL structure
- Sitemap presence

### 7. Security Headers (10% of total score)
- HSTS implementation
- Content Security Policy
- X-Content-Type-Options
- X-Frame-Options
- XSS Protection
- Referrer Policy

### 8. Accessibility (5% of total score)
- ARIA labels
- Color contrast
- Keyboard navigation
- Alt text presence
- Semantic HTML

### 9. Content Quality (5% of total score)
- Content freshness
- Readability
- Engagement elements
- Media optimization

## Lead Classification

Based on the overall score, websites are classified as:
- **80-100**: Excellent (Low-Priority Lead)
- **65-79**: Good (Maintenance Lead)
- **50-64**: Average (Potential Lead)
- **35-49**: Outdated (Potential Lead)
- **0-34**: Poor (High-Priority Lead)

## Technical Stack

### Frontend
- HTML5
- Tailwind CSS
- Vanilla JavaScript
- Responsive Design

### Backend
- Python 3.12
- Flask
- BeautifulSoup4
- Requests
- CORS support

## Deployment

The application is deployed on Render.com with:
- Frontend static site hosting
- Backend Python/Flask API service
- Automatic HTTPS
- Continuous deployment from GitHub

### URLs after deployment:
- Frontend: `https://website-grader-frontend.onrender.com`
- Backend API: `https://website-grader-api.onrender.com`

## Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/insinexzy/Website-Grader.git
   cd Website-Grader
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the backend:
   ```bash
   python app.py
   ```

4. Serve the frontend:
   ```bash
   python -m http.server 8000
   ```

5. Access the application at `http://localhost:8000`

## API Endpoints

### POST /api/analyze
Analyzes a website and returns comprehensive results.

Request body:
```json
{
    "url": "https://example.com"
}
```

Response includes:
- Overall score and classification
- Category-wise scores and details
- Technical metrics
- Improvement suggestions

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

MIT License - feel free to use this tool for any purpose.

## Author

Website Grader Team 
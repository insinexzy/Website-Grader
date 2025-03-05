#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Grader v4 - A comprehensive tool for analyzing and scoring websites.
This tool evaluates websites based on various technical and design aspects,
helping identify potential leads for web development and design services.

Author: Website Grader Team
Version: 4.0
"""

import sys
import requests
from bs4 import BeautifulSoup
import re
import time
import json
import ssl
import socket
from urllib.parse import urlparse, urljoin
from datetime import datetime
import logging
from tabulate import tabulate
import concurrent.futures
import tldextract
import validators
import colorama
from colorama import Fore, Style

# Initialize colorama for cross-platform colored terminal output
colorama.init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("website_grader.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebsiteGraderV4:
    """
    A comprehensive website grader that analyzes and scores websites based on
    various technical and design aspects.
    """
    
    def __init__(self, timeout=20, max_retries=2, user_agent=None):
        """
        Initialize the WebsiteGrader with configuration parameters.
        
        Args:
            timeout (int): Request timeout in seconds
            max_retries (int): Maximum number of retry attempts for failed requests
            user_agent (str): Custom user agent string for requests
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        # Define headers for requests
        self.headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        
        # Define category weights for scoring (total = 100)
        self.category_weights = {
            'ssl': 10,        # Basic security
            'mobile': 15,     # Mobile responsiveness
            'page_speed': 15, # Performance
            'tech_stack': 25, # Modern technology (highest weight)
            'ui_quality': 10, # User interface
            'seo': 5,        # Search optimization
            'security': 10,   # Advanced security
            'accessibility': 5, # A11y
            'content': 5      # Content quality
        }
        
        # Initialize results dictionary
        self.results = {}
        
    def _get_with_retry(self, url, headers=None):
        """
        Perform an HTTP GET request with retry logic.
        
        Args:
            url (str): The URL to request
            headers (dict): Optional custom headers
            
        Returns:
            requests.Response: The response object
            
        Raises:
            Exception: If all retry attempts fail
        """
        headers = headers or self.headers
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                response = requests.get(url, headers=headers, timeout=self.timeout, verify=True)
                return response
            except (requests.RequestException, ssl.SSLError) as e:
                retry_count += 1
                if retry_count > self.max_retries:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts: {str(e)}")
                    raise
                logger.warning(f"Retry {retry_count}/{self.max_retries} for {url}: {str(e)}")
                time.sleep(1)  # Wait before retrying
                
    def analyze_website(self, url):
        """
        Analyze a website and return comprehensive results.
        
        Args:
            url (str): The URL to analyze
            
        Returns:
            dict: Analysis results with scores and details
        """
        logger.info(f"Analyzing {url}...")
        print(f"\nAnalyzing {url}...")
        
        try:
            # Measure initial load time
            start_time = time.time()
            response = self._get_with_retry(url)
            load_time = time.time() - start_time
            
            if response.status_code == 403:
                print(f"\n{Fore.RED}Error: Access Forbidden (403) for {url}")
                print("This website has blocked automated access. This typically happens with enterprise-level websites")
                print("that have strict security measures against automated tools.")
                print(f"Skipping analysis.{Style.RESET_ALL}\n")
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            html = response.text

            # Initialize results dictionary
            self.results[url] = {
                'url': url,
                'load_time': load_time,
                'status_code': response.status_code,
                'categories': {},
                'total_score': 0,
                'max_score': 100,  # New fixed max score
                'percentage': 0,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Run all checks
            self.results[url]['categories']['ssl'] = self.check_ssl(url, response, soup, html)
            self.results[url]['categories']['mobile'] = self.check_mobile(url, response, soup, html)
            self.results[url]['categories']['page_speed'] = self.check_page_speed(url, response, soup, html)
            self.results[url]['categories']['tech_stack'] = self.analyze_tech_stack(url, response, soup, html)
            self.results[url]['categories']['ui_quality'] = self.check_ui_quality(url, response, soup, html)
            self.results[url]['categories']['seo'] = self.check_seo(url, response, soup, html)
            self.results[url]['categories']['security'] = self.check_security_headers(url, response, soup, html)
            self.results[url]['categories']['accessibility'] = self.check_accessibility(url, response, soup, html)
            self.results[url]['categories']['content'] = self.check_content_quality(url, response, soup, html)
            
            # Calculate total score
            total_score = 0
            
            for category, result in self.results[url]['categories'].items():
                weight = self.category_weights.get(category, 1.0)
                # Normalize each category score to be out of 100 before applying weight
                category_percentage = (result['score'] / result['max_score']) * 100
                total_score += (category_percentage * weight) / 100
                
            self.results[url]['total_score'] = round(total_score, 1)
            self.results[url]['max_score'] = 100
            self.results[url]['percentage'] = total_score  # Percentage is now the same as total_score
            
            # Determine classification based on percentage
            if total_score >= 80:
                classification = "Excellent"
                lead_potential = "Low-Priority Lead"
            elif total_score >= 65:
                classification = "Good"
                lead_potential = "Maintenance Lead"
            elif total_score >= 50:
                classification = "Average"
                lead_potential = "Potential Lead"
            elif total_score >= 35:
                classification = "Outdated"
                lead_potential = "Potential Lead"
            else:
                classification = "Poor"
                lead_potential = "High-Priority Lead"
                
            self.results[url]['classification'] = classification
            self.results[url]['lead_potential'] = lead_potential
            
            return self.results[url]
            
        except Exception as e:
            logger.error(f"Error analyzing {url}: {str(e)}")
            print(f"{Fore.RED}Error analyzing {url}: {str(e)}{Style.RESET_ALL}")
            self.results[url] = {
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            return self.results[url]
            
    def get_max_total_score(self):
        """
        Get the maximum possible total score.
        
        Returns:
            float: Maximum possible score
        """
        return sum(self.category_weights.values()) * 10  # Assuming each category has max score of 10
        
    def check_ssl(self, url, response, soup, html):
        """
        Check SSL certificate and HTTPS implementation.
        
        Args:
            url (str): The URL being analyzed
            response (requests.Response): The response object
            soup (BeautifulSoup): Parsed HTML
            html (str): Raw HTML content
            
        Returns:
            dict: Results of SSL check with score and details
        """
        logger.info(f"Checking SSL for {url}")
        result = {
            'score': 0,
            'max_score': 5,
            'details': [],
            'issues': []
        }
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Check if using HTTPS
        if url.startswith('https://'):
            result['score'] += 2
            result['details'].append("Website uses HTTPS")
        else:
            result['issues'].append("Website does not use HTTPS")
            
        # Check SSL certificate details
        try:
            # Create a context with the protocol we want to use
            context = ssl.create_default_context()
            
            with socket.create_connection((domain, 443), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check certificate validity
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                    now = datetime.now()
                    
                    # Certificate is valid
                    if now > not_before and now < not_after:
                        result['score'] += 1
                        result['details'].append(f"SSL certificate is valid until {not_after.strftime('%Y-%m-%d')}")
                        
                        # Check days until expiration
                        days_left = (not_after - now).days
                        if days_left > 90:
                            result['score'] += 1
                            result['details'].append(f"SSL certificate expires in {days_left} days (>90 days)")
                        else:
                            result['issues'].append(f"SSL certificate expires soon ({days_left} days)")
                    else:
                        result['issues'].append("SSL certificate is not valid")
                        
                    # Check certificate issuer
                    issuer = dict(x[0] for x in cert['issuer'])
                    organization = issuer.get('organizationName', 'Unknown')
                    result['details'].append(f"Certificate issued by: {organization}")
                    
                    # Check if it's an EV certificate
                    if 'jurisdictionCountryName' in cert.get('subject', []):
                        result['score'] += 1
                        result['details'].append("Using Extended Validation (EV) certificate")
                        
        except (socket.gaierror, socket.timeout, ssl.SSLError, ConnectionRefusedError) as e:
            if url.startswith('https://'):
                result['issues'].append(f"SSL certificate check failed: {str(e)}")
            else:
                result['issues'].append("No SSL certificate (using HTTP)")
                
        # Check for mixed content
        if url.startswith('https://'):
            mixed_content_patterns = [
                r'http:\/\/[^"\']*\.(jpg|jpeg|png|gif|css|js)',
                r'src\s*=\s*["\']http:\/\/',
                r'href\s*=\s*["\']http:\/\/'
            ]
            
            has_mixed_content = False
            for pattern in mixed_content_patterns:
                if re.search(pattern, html, re.IGNORECASE):
                    has_mixed_content = True
                    break
                    
            if not has_mixed_content:
                result['score'] += 1
                result['details'].append("No mixed content detected")
            else:
                result['issues'].append("Mixed content detected (HTTP resources on HTTPS page)")
                
        return result 

    def check_mobile(self, url, response, soup, html):
        """
        Check mobile-friendliness of the website.
        
        Args:
            url (str): The URL being analyzed
            response (requests.Response): The response object
            soup (BeautifulSoup): Parsed HTML
            html (str): Raw HTML content
            
        Returns:
            dict: Results of mobile-friendliness check with score and details
        """
        logger.info(f"Checking mobile-friendliness for {url}")
        result = {
            'score': 0,
            'max_score': 5,
            'details': [],
            'issues': []
        }
        
        # Check viewport meta tag
        viewport = soup.find('meta', {'name': 'viewport'})
        if viewport:
            viewport_content = viewport.get('content', '')
            result['score'] += 1
            result['details'].append(f"Viewport meta tag: {viewport_content}")
            
            # Check if viewport content is properly configured
            if 'width=device-width' in viewport_content and 'initial-scale=1' in viewport_content:
                result['score'] += 1
                result['details'].append("Viewport properly configured with device-width and initial-scale")
            else:
                result['issues'].append("Viewport meta tag exists but may not be properly configured")
        else:
            result['issues'].append("No viewport meta tag found (not mobile-friendly)")
            
        # Check for responsive design patterns
        media_queries_count = len(re.findall(r'@media\s*\([^{]+\)\s*{', html))
        if media_queries_count > 0:
            result['score'] += 1
            result['details'].append(f"Found {media_queries_count} media queries for responsive design")
        else:
            result['issues'].append("No media queries found for responsive design")
            
        # Check for mobile-specific meta tags
        mobile_meta_tags = [
            soup.find('meta', {'name': 'apple-mobile-web-app-capable'}),
            soup.find('meta', {'name': 'apple-mobile-web-app-status-bar-style'}),
            soup.find('meta', {'name': 'format-detection'}),
            soup.find('meta', {'name': 'mobile-web-app-capable'})
        ]
        
        mobile_meta_count = sum(1 for tag in mobile_meta_tags if tag)
        if mobile_meta_count > 0:
            result['score'] += 0.5
            result['details'].append(f"Found {mobile_meta_count} mobile-specific meta tags")
            
        # Check for touch icons
        touch_icons = [
            soup.find('link', {'rel': 'apple-touch-icon'}),
            soup.find('link', {'rel': 'apple-touch-icon-precomposed'}),
            soup.find('link', {'rel': 'icon', 'sizes': True})
        ]
        
        touch_icon_count = sum(1 for icon in touch_icons if icon)
        if touch_icon_count > 0:
            result['score'] += 0.5
            result['details'].append(f"Found {touch_icon_count} touch icons for mobile devices")
            
        # Check for responsive images
        responsive_img_patterns = [
            r'<img[^>]+srcset=',
            r'<img[^>]+sizes=',
            r'<picture>',
            r'<source[^>]+media='
        ]
        
        responsive_img_count = sum(len(re.findall(pattern, html)) for pattern in responsive_img_patterns)
        if responsive_img_count > 0:
            result['score'] += 1
            result['details'].append(f"Found {responsive_img_count} responsive image techniques")
        else:
            result['issues'].append("No responsive image techniques detected")
            
        # Check font size for readability
        small_font_patterns = [
            r'font-size\s*:\s*(0\.([0-8])|[0-8])px',
            r'font-size\s*:\s*(0\.([0-8])|[0-8])em',
            r'font-size\s*:\s*(0\.([0-8])|[0-8])rem'
        ]
        
        small_font_count = sum(len(re.findall(pattern, html)) for pattern in small_font_patterns)
        if small_font_count == 0:
            result['details'].append("No extremely small font sizes detected")
        else:
            result['issues'].append(f"Found {small_font_count} instances of very small font sizes")
            
        # Check for mobile frameworks
        mobile_frameworks = []
        
        if re.search(r'(jquery\.mobile|jquery-mobile)', html, re.IGNORECASE):
            mobile_frameworks.append("jQuery Mobile")
        if re.search(r'(ionic\.bundle|ionic-bundle)', html, re.IGNORECASE):
            mobile_frameworks.append("Ionic")
        if re.search(r'(framework7|framework-7)', html, re.IGNORECASE):
            mobile_frameworks.append("Framework7")
        if re.search(r'(onsen)', html, re.IGNORECASE):
            mobile_frameworks.append("Onsen UI")
        if re.search(r'(amp-boilerplate|googleamp)', html, re.IGNORECASE):
            mobile_frameworks.append("Google AMP")
            
        if mobile_frameworks:
            result['score'] = min(result['score'] + len(mobile_frameworks) * 0.5, result['max_score'])
            for framework in mobile_frameworks:
                result['details'].append(f"Using mobile framework: {framework}")
                
        return result 

    def check_page_speed(self, url, response, soup, html):
        """
        Check page speed and performance optimizations.
        
        Args:
            url (str): The URL being analyzed
            response (requests.Response): The response object
            soup (BeautifulSoup): Parsed HTML
            html (str): Raw HTML content
            
        Returns:
            dict: Results of page speed check with score and details
        """
        logger.info(f"Checking page speed for {url}")
        result = {
            'score': 0,
            'max_score': 5,
            'details': [],
            'issues': []
        }
        
        # Check load time
        load_time = response.elapsed.total_seconds()
        result['details'].append(f"Initial load time: {load_time:.2f} seconds")
        
        if load_time < 1.0:
            result['score'] += 2
            result['details'].append("Excellent load time (< 1 second)")
        elif load_time < 2.0:
            result['score'] += 1.5
            result['details'].append("Good load time (< 2 seconds)")
        elif load_time < 3.0:
            result['score'] += 1
            result['details'].append("Average load time (< 3 seconds)")
        elif load_time < 5.0:
            result['score'] += 0.5
            result['details'].append("Slow load time (< 5 seconds)")
        else:
            result['issues'].append(f"Very slow load time ({load_time:.2f} seconds)")
            
        # Check page size
        page_size = len(html)
        size_kb = page_size / 1024
        result['details'].append(f"HTML size: {size_kb:.2f} KB")
        
        if size_kb < 50:
            result['score'] += 1
            result['details'].append("Small HTML size (< 50 KB)")
        elif size_kb < 100:
            result['score'] += 0.5
            result['details'].append("Moderate HTML size (< 100 KB)")
        else:
            result['issues'].append(f"Large HTML size ({size_kb:.2f} KB)")
            
        # Check for resource hints
        resource_hints = [
            ('preload', soup.find_all('link', {'rel': 'preload'})),
            ('prefetch', soup.find_all('link', {'rel': 'prefetch'})),
            ('preconnect', soup.find_all('link', {'rel': 'preconnect'})),
            ('dns-prefetch', soup.find_all('link', {'rel': 'dns-prefetch'}))
        ]
        
        resource_hints_count = 0
        for hint_type, hints in resource_hints:
            if hints:
                resource_hints_count += len(hints)
                result['details'].append(f"Using {hint_type} for {len(hints)} resources")
                
        if resource_hints_count > 0:
            result['score'] += min(resource_hints_count * 0.2, 1)
            
        # Check for minified resources
        js_files = soup.find_all('script', src=True)
        css_files = soup.find_all('link', {'rel': 'stylesheet'})
        
        minified_js = sum(1 for script in js_files if '.min.js' in script.get('src', ''))
        minified_css = sum(1 for link in css_files if '.min.css' in link.get('href', ''))
        
        if minified_js > 0 or minified_css > 0:
            result['score'] += 0.5
            result['details'].append(f"Using minified resources: {minified_js} JS files, {minified_css} CSS files")
        else:
            result['issues'].append("No minified JS or CSS resources detected")
            
        # Check for image optimization
        img_tags = soup.find_all('img')
        img_with_alt = sum(1 for img in img_tags if img.get('alt'))
        img_with_lazy = sum(1 for img in img_tags if img.get('loading') == 'lazy' or 'lazyload' in img.get('class', []))
        
        if img_tags:
            alt_percentage = (img_with_alt / len(img_tags)) * 100 if img_tags else 0
            lazy_percentage = (img_with_lazy / len(img_tags)) * 100 if img_tags else 0
            
            result['details'].append(f"Images with alt text: {alt_percentage:.1f}%")
            result['details'].append(f"Images with lazy loading: {lazy_percentage:.1f}%")
            
            if lazy_percentage >= 50:
                result['score'] += 0.5
                result['details'].append("Good use of lazy loading for images")
            elif img_with_lazy > 0:
                result['details'].append("Some images use lazy loading")
            else:
                result['issues'].append("No lazy loading detected for images")
                
        # Check for browser caching headers
        cache_headers = [
            ('Cache-Control', response.headers.get('Cache-Control')),
            ('ETag', response.headers.get('ETag')),
            ('Expires', response.headers.get('Expires')),
            ('Last-Modified', response.headers.get('Last-Modified'))
        ]
        
        cache_headers_count = sum(1 for _, value in cache_headers if value)
        if cache_headers_count >= 2:
            result['score'] += 0.5
            result['details'].append(f"Using {cache_headers_count} browser caching headers")
        elif cache_headers_count > 0:
            result['details'].append(f"Using {cache_headers_count} browser caching header")
        else:
            result['issues'].append("No browser caching headers detected")
            
        # Check for compression
        compression = response.headers.get('Content-Encoding')
        if compression:
            result['score'] += 0.5
            result['details'].append(f"Using {compression} compression")
        else:
            result['issues'].append("No compression detected")
            
        # Check for render-blocking resources
        render_blocking_js = sum(1 for script in js_files if not script.get('async') and not script.get('defer') and script.get('src') and not script.get('src').startswith('data:'))
        render_blocking_css = sum(1 for link in css_files if not link.get('media') or link.get('media') == 'all')
        
        if render_blocking_js == 0 and render_blocking_css == 0:
            result['score'] += 0.5
            result['details'].append("No render-blocking resources detected")
        else:
            result['issues'].append(f"Found render-blocking resources: {render_blocking_js} JS, {render_blocking_css} CSS")
            
        return result 

    def analyze_tech_stack(self, url, response, soup, html):
        """
        Analyze the technology stack used by the website.
        
        Args:
            url (str): The URL being analyzed
            response (requests.Response): The response object
            soup (BeautifulSoup): Parsed HTML
            html (str): Raw HTML content
            
        Returns:
            dict: Results of tech stack analysis with score and details
        """
        logger.info(f"Analyzing tech stack for {url}")
        result = {
            'score': 0,
            'max_score': 10,  # Keep internal score out of 10 for simplicity
            'details': [],
            'issues': []
        }

        # Modern Framework Detection (Higher scores for modern frameworks)
        modern_frameworks = {
            'next': {'pattern': r'__NEXT_DATA__|next/router|next-page|next\.js', 'score': 5, 'name': 'Next.js'},
            'react': {'pattern': r'react\.development|react\.production|reactjs|__REACT', 'score': 4, 'name': 'React'},
            'vue3': {'pattern': r'vue@3|Vue\.createApp|vue3', 'score': 4, 'name': 'Vue 3'},
            'nuxt': {'pattern': r'__NUXT_|nuxt\.js|nuxtjs', 'score': 5, 'name': 'Nuxt.js'},
            'angular': {'pattern': r'ng-version|angular\.min\.js|angular\.js', 'score': 4, 'name': 'Angular'},
            'svelte': {'pattern': r'svelte-|svelte\.min\.js', 'score': 4, 'name': 'Svelte'},
            'remix': {'pattern': r'remix-run|remix\.config', 'score': 5, 'name': 'Remix'},
            'gatsby': {'pattern': r'gatsby-|___gatsby', 'score': 4, 'name': 'Gatsby'}
        }

        # Legacy Framework Detection (Negative scores for outdated tech)
        legacy_frameworks = {
            'jquery': {'pattern': r'jquery\.min\.js|jquery-|jQuery', 'score': -3, 'name': 'jQuery'},
            'bootstrap': {'pattern': r'bootstrap\.min\.js|bootstrap\.min\.css', 'score': -1, 'name': 'Bootstrap 3/4'},
            'wordpress': {'pattern': r'wp-content|wp-includes|wordpress', 'score': -2, 'name': 'WordPress'},
            'php': {'pattern': r'\.php"|\.php\'|powered by php', 'score': -2, 'name': 'PHP'},
            'aspnet': {'pattern': r'\.aspx|\.asp|webform', 'score': -2, 'name': 'ASP.NET WebForms'}
        }

        # Modern Features Detection (Bonus points)
        modern_features = {
            'typescript': {'pattern': r'\.tsx?"|\.tsx\'|typescript', 'score': 2, 'name': 'TypeScript'},
            'es6_plus': {'pattern': r'const |let |=>\s*{|\basync\b|\bawait\b', 'score': 2, 'name': 'ES6+ Features'},
            'web_components': {'pattern': r'customElements|shadow-root|:host{', 'score': 2, 'name': 'Web Components'},
            'module_bundler': {'pattern': r'webpack|vite|parcel|rollup', 'score': 1, 'name': 'Modern Build Tools'}
        }

        # Performance Optimizations (Bonus points)
        optimizations = {
            'lazy_loading': {'pattern': r'loading="lazy"|lazy-load|React\.lazy', 'score': 1, 'name': 'Lazy Loading'},
            'code_splitting': {'pattern': r'chunk\.|dynamic import|React\.Suspense', 'score': 1, 'name': 'Code Splitting'},
            'service_worker': {'pattern': r'serviceWorker|workbox|navigator\.serviceWorker', 'score': 1, 'name': 'Service Worker'},
            'pwa': {'pattern': r'manifest\.json|progressive web app|PWA', 'score': 1, 'name': 'PWA Support'}
        }

        # Check for frameworks and features
        modern_detected = False
        legacy_detected = False

        for category in [modern_frameworks, legacy_frameworks, modern_features, optimizations]:
            for tech, data in category.items():
                if re.search(data['pattern'], str(html), re.I):
                    result['score'] += data['score']
                    result['details'].append(f"Detected {data['name']}")
                    if category == modern_frameworks:
                        modern_detected = True
                    elif category == legacy_frameworks:
                        legacy_detected = True

        # Additional penalties for mixing modern and legacy
        if modern_detected and legacy_detected:
            result['score'] -= 2
            result['issues'].append("Mixing modern and legacy technologies (not recommended)")

        # Normalize score (but allow negative scores for very outdated sites)
        result['score'] = max(-5, min(result['score'], result['max_score']))

        # Add recommendations based on findings
        if result['score'] < 0:
            result['issues'].append("Website uses severely outdated technologies")
            result['issues'].append("Urgent need for complete modernization")
        elif result['score'] < 3:
            result['issues'].append("Consider upgrading to modern frameworks like React, Vue, or Angular")
            result['issues'].append("Implement modern JavaScript features and build tools")
        elif result['score'] < 7:
            result['issues'].append("Consider adding more modern optimizations like code splitting and PWA support")

        return result

    def check_ui_quality(self, url, response, soup, html):
        """
        Check UI quality and design aspects of the website.
        
        Args:
            url (str): The URL being analyzed
            response (requests.Response): The response object
            soup (BeautifulSoup): Parsed HTML
            html (str): Raw HTML content
            
        Returns:
            dict: Results of UI quality check with score and details
        """
        logger.info(f"Checking UI quality for {url}")
        result = {
            'score': 0,
            'max_score': 5,
            'details': [],
            'issues': []
        }
        
        # Check for favicon
        favicon = soup.find('link', {'rel': ['icon', 'shortcut icon']})
        if favicon:
            result['score'] += 0.5
            result['details'].append("Website has a favicon")
        else:
            result['issues'].append("No favicon detected")
            
        # Check for consistent heading structure
        headings = []
        for i in range(1, 7):
            headings.append(len(soup.find_all(f'h{i}')))
            
        # Check if headings are in proper order (h1 -> h2 -> h3, etc.)
        has_h1 = headings[0] > 0
        if has_h1:
            result['score'] += 0.5
            result['details'].append(f"Website has {headings[0]} H1 heading(s)")
        else:
            result['issues'].append("No H1 heading found")
            
        # Check for proper heading hierarchy
        proper_hierarchy = True
        for i in range(len(headings) - 1):
            if headings[i] == 0 and headings[i+1] > 0:
                proper_hierarchy = False
                break
                
        if proper_hierarchy:
            result['score'] += 0.5
            result['details'].append("Proper heading hierarchy")
        else:
            result['issues'].append("Improper heading hierarchy (e.g., H3 without H2)")
            
        # Check for consistent font usage
        font_families = re.findall(r'font-family\s*:\s*([^;}]+)[;}]', html)
        unique_fonts = set()
        for font in font_families:
            # Extract the first font in each font-family declaration
            first_font = font.split(',')[0].strip().lower()
            if first_font:
                unique_fonts.add(first_font)
                
        if len(unique_fonts) <= 3:
            result['score'] += 0.5
            result['details'].append(f"Consistent font usage ({len(unique_fonts)} primary fonts)")
        else:
            result['issues'].append(f"Too many different fonts ({len(unique_fonts)} primary fonts)")
            
        # Check for color consistency
        color_values = re.findall(r'(?:color|background-color|border-color)\s*:\s*([^;}]+)[;}]', html)
        unique_colors = set()
        for color in color_values:
            color = color.strip().lower()
            if color and color != 'inherit' and color != 'transparent':
                unique_colors.add(color)
                
        if len(unique_colors) <= 10:
            result['score'] += 0.5
            result['details'].append(f"Consistent color palette ({len(unique_colors)} colors)")
        else:
            result['issues'].append(f"Inconsistent color usage ({len(unique_colors)} different colors)")
            
        # Check for responsive images
        img_tags = soup.find_all('img')
        responsive_img_count = sum(1 for img in img_tags if img.get('srcset') or img.get('sizes'))
        
        if img_tags:
            responsive_percentage = (responsive_img_count / len(img_tags)) * 100 if img_tags else 0
            if responsive_percentage >= 50:
                result['score'] += 0.5
                result['details'].append(f"Good use of responsive images ({responsive_percentage:.1f}%)")
            elif responsive_img_count > 0:
                result['details'].append(f"Some responsive images ({responsive_percentage:.1f}%)")
            else:
                result['issues'].append("No responsive images detected")
                
        # Check for modern CSS features
        modern_css_features = {
            'Flexbox': [r'display\s*:\s*flex', r'flex-'],
            'Grid': [r'display\s*:\s*grid', r'grid-'],
            'CSS Variables': [r'--[a-zA-Z0-9-_]+', r'var\(--'],
            'Media Queries': [r'@media'],
            'Transitions': [r'transition'],
            'Animations': [r'animation', r'@keyframes'],
            'Transforms': [r'transform'],
            'Gradients': [r'linear-gradient', r'radial-gradient']
        }
        
        detected_css_features = []
        for feature, patterns in modern_css_features.items():
            for pattern in patterns:
                if re.search(pattern, html, re.IGNORECASE):
                    detected_css_features.append(feature)
                    break
                    
        if len(detected_css_features) >= 3:
            result['score'] += 1
            result['details'].append(f"Using modern CSS features: {', '.join(detected_css_features[:3])}")
        elif detected_css_features:
            result['score'] += 0.5
            result['details'].append(f"Using some modern CSS features: {', '.join(detected_css_features)}")
        else:
            result['issues'].append("No modern CSS features detected")
            
        # Check for whitespace and layout
        whitespace_patterns = [
            r'margin\s*:', r'padding\s*:',
            r'margin-(top|right|bottom|left)\s*:',
            r'padding-(top|right|bottom|left)\s*:'
        ]
        
        whitespace_count = sum(len(re.findall(pattern, html)) for pattern in whitespace_patterns)
        if whitespace_count > 20:
            result['score'] += 0.5
            result['details'].append("Good use of whitespace in layout")
        elif whitespace_count > 10:
            result['details'].append("Some use of whitespace in layout")
        else:
            result['issues'].append("Limited use of whitespace in layout")
            
        # Check for mobile menu
        mobile_menu_patterns = [
            r'navbar-toggler', r'hamburger', r'menu-toggle',
            r'mobile-menu', r'nav-toggle', r'menu-icon'
        ]
        
        has_mobile_menu = any(re.search(pattern, html, re.IGNORECASE) for pattern in mobile_menu_patterns)
        if has_mobile_menu:
            result['score'] += 0.5
            result['details'].append("Mobile menu detected")
        else:
            result['issues'].append("No mobile menu detected")
            
        return result 

    def check_seo(self, url, response, soup, html):
        """
        Check SEO optimization of the website.
        
        Args:
            url (str): The URL being analyzed
            response (requests.Response): The response object
            soup (BeautifulSoup): Parsed HTML
            html (str): Raw HTML content
            
        Returns:
            dict: Results of SEO check with score and details
        """
        logger.info(f"Checking SEO for {url}")
        result = {
            'score': 0,
            'max_score': 5,
            'details': [],
            'issues': []
        }
        
        # Check title tag
        title = soup.find('title')
        if title and title.text.strip():
            title_text = title.text.strip()
            result['score'] += 0.5
            result['details'].append(f"Title tag: {title_text}")
            
            # Check title length (Google typically displays the first 50-60 characters)
            if 10 <= len(title_text) <= 60:
                result['score'] += 0.5
                result['details'].append(f"Title length is optimal ({len(title_text)} characters)")
            elif len(title_text) < 10:
                result['issues'].append(f"Title is too short ({len(title_text)} characters)")
            else:
                result['issues'].append(f"Title is too long ({len(title_text)} characters)")
        else:
            result['issues'].append("Missing title tag")
            
        # Check meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content', '').strip():
            desc_content = meta_desc.get('content', '').strip()
            result['score'] += 0.5
            result['details'].append(f"Meta description: {desc_content[:100]}...")
            
            # Check description length (Google typically displays around 155-160 characters)
            if 50 <= len(desc_content) <= 160:
                result['score'] += 0.5
                result['details'].append(f"Meta description length is optimal ({len(desc_content)} characters)")
            elif len(desc_content) < 50:
                result['issues'].append(f"Meta description is too short ({len(desc_content)} characters)")
            else:
                result['issues'].append(f"Meta description is too long ({len(desc_content)} characters)")
        else:
            result['issues'].append("Missing meta description")
            
        # Check for canonical URL
        canonical = soup.find('link', {'rel': 'canonical'})
        if canonical and canonical.get('href'):
            result['score'] += 0.5
            result['details'].append(f"Canonical URL: {canonical.get('href')}")
        else:
            result['issues'].append("No canonical URL specified")
            
        # Check for heading structure
        h1_tags = soup.find_all('h1')
        if h1_tags:
            if len(h1_tags) == 1:
                result['score'] += 0.5
                result['details'].append("Single H1 tag (recommended)")
            else:
                result['issues'].append(f"Multiple H1 tags found ({len(h1_tags)})")
                
            # Check if H1 contains keywords from title
            if title and h1_tags[0].text.strip():
                title_words = set(re.findall(r'\w+', title.text.lower()))
                h1_words = set(re.findall(r'\w+', h1_tags[0].text.lower()))
                common_words = title_words.intersection(h1_words)
                
                if len(common_words) >= 2:
                    result['score'] += 0.25
                    result['details'].append("H1 contains keywords from title")
        else:
            result['issues'].append("No H1 tag found")
            
        # Check for image alt text
        img_tags = soup.find_all('img')
        img_with_alt = sum(1 for img in img_tags if img.get('alt'))
        
        if img_tags:
            alt_percentage = (img_with_alt / len(img_tags)) * 100 if img_tags else 0
            result['details'].append(f"Images with alt text: {alt_percentage:.1f}%")
            
            if alt_percentage >= 80:
                result['score'] += 0.5
                result['details'].append("Good use of alt text for images")
            elif alt_percentage >= 50:
                result['score'] += 0.25
                result['details'].append("Moderate use of alt text for images")
            else:
                result['issues'].append("Poor use of alt text for images")
                
        # Check for structured data
        structured_data_patterns = [
            r'application/ld\+json',
            r'itemscope',
            r'itemtype',
            r'schema.org'
        ]
        
        has_structured_data = any(re.search(pattern, html, re.IGNORECASE) for pattern in structured_data_patterns)
        if has_structured_data:
            result['score'] += 0.5
            result['details'].append("Structured data (Schema.org) detected")
        else:
            result['issues'].append("No structured data detected")
            
        # Check for Open Graph tags
        og_tags = soup.find_all('meta', {'property': re.compile(r'^og:')})
        if og_tags:
            result['score'] += 0.25
            result['details'].append(f"Open Graph tags: {len(og_tags)}")
        else:
            result['issues'].append("No Open Graph tags found")
            
        # Check for Twitter Card tags
        twitter_tags = soup.find_all('meta', {'name': re.compile(r'^twitter:')})
        if twitter_tags:
            result['score'] += 0.25
            result['details'].append(f"Twitter Card tags: {len(twitter_tags)}")
        else:
            result['issues'].append("No Twitter Card tags found")
            
        # Check URL structure
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Check for clean URL structure (no query parameters in main URL)
        if not parsed_url.query:
            result['score'] += 0.25
            result['details'].append("Clean URL structure (no query parameters)")
            
        # Check for keywords in URL
        if title:
            title_words = set(re.findall(r'\w+', title.text.lower()))
            path_words = set(re.findall(r'\w+', path.lower()))
            common_words = title_words.intersection(path_words)
            
            if len(common_words) >= 1:
                result['score'] += 0.25
                result['details'].append("URL contains keywords from title")
                
        # Check for robots meta tag
        robots = soup.find('meta', {'name': 'robots'})
        if robots:
            robots_content = robots.get('content', '').lower()
            result['details'].append(f"Robots meta tag: {robots_content}")
            
            if 'noindex' in robots_content or 'nofollow' in robots_content:
                result['issues'].append("Page is set to noindex or nofollow")
        else:
            result['details'].append("No robots meta tag (defaults to index,follow)")
            
        # Check for sitemap reference
        sitemap_patterns = [
            r'<a[^>]*href=["\'][^"\']*sitemap\.xml["\']',
            r'<link[^>]*href=["\'][^"\']*sitemap\.xml["\']'
        ]
        
        has_sitemap_link = any(re.search(pattern, html, re.IGNORECASE) for pattern in sitemap_patterns)
        if has_sitemap_link:
            result['score'] += 0.25
            result['details'].append("Sitemap link found in HTML")
            
        return result 

    def check_security_headers(self, url, response, soup, html):
        """
        Check security headers and features of the website.
        
        Args:
            url (str): The URL being analyzed
            response (requests.Response): The response object
            soup (BeautifulSoup): Parsed HTML
            html (str): Raw HTML content
            
        Returns:
            dict: Results of security headers check with score and details
        """
        logger.info(f"Checking security headers for {url}")
        result = {
            'score': 0,
            'max_score': 5,
            'details': [],
            'issues': []
        }
        
        # Check for HTTPS
        if url.startswith('https://'):
            result['score'] += 1
            result['details'].append("Website uses HTTPS")
        else:
            result['issues'].append("Website does not use HTTPS (major security issue)")
            
        # Check for security headers
        security_headers = {
            'Strict-Transport-Security': "HSTS forces HTTPS connections",
            'Content-Security-Policy': "CSP prevents XSS attacks",
            'X-Content-Type-Options': "Prevents MIME-type sniffing",
            'X-Frame-Options': "Prevents clickjacking attacks",
            'X-XSS-Protection': "Provides XSS protection for older browsers",
            'Referrer-Policy': "Controls referrer information",
            'Feature-Policy': "Controls browser features",
            'Permissions-Policy': "Controls browser permissions"
        }
        
        headers_found = []
        for header, description in security_headers.items():
            if header in response.headers:
                headers_found.append(header)
                result['details'].append(f"{header}: {response.headers[header]}")
                
        # Score based on number of security headers
        if len(headers_found) >= 5:
            result['score'] += 2
            result['details'].append("Excellent security headers implementation")
        elif len(headers_found) >= 3:
            result['score'] += 1.5
            result['details'].append("Good security headers implementation")
        elif len(headers_found) >= 1:
            result['score'] += 1
            result['details'].append("Basic security headers implementation")
        else:
            result['issues'].append("No security headers implemented")
            
        # Check for missing important headers
        important_headers = ['Strict-Transport-Security', 'Content-Security-Policy', 'X-Content-Type-Options']
        missing_important = [h for h in important_headers if h not in headers_found]
        if missing_important:
            result['issues'].append(f"Missing important security headers: {', '.join(missing_important)}")
            
        # Check for cookies security
        cookies = response.cookies
        secure_cookies = sum(1 for cookie in cookies if cookie.secure)
        httponly_cookies = sum(1 for cookie in cookies if cookie.has_nonstandard_attr('HttpOnly'))
        samesite_cookies = sum(1 for cookie in cookies if cookie.has_nonstandard_attr('SameSite'))
        
        if cookies:
            result['details'].append(f"Total cookies: {len(cookies)}")
            
            # Calculate percentage of secure cookies
            secure_percentage = (secure_cookies / len(cookies)) * 100 if cookies else 0
            httponly_percentage = (httponly_cookies / len(cookies)) * 100 if cookies else 0
            
            if secure_percentage == 100 and httponly_percentage == 100:
                result['score'] += 1
                result['details'].append("All cookies use Secure and HttpOnly flags")
            elif secure_percentage >= 50 and httponly_percentage >= 50:
                result['score'] += 0.5
                result['details'].append(f"Some cookies use security flags (Secure: {secure_percentage:.1f}%, HttpOnly: {httponly_percentage:.1f}%)")
            else:
                result['issues'].append(f"Poor cookie security (Secure: {secure_percentage:.1f}%, HttpOnly: {httponly_percentage:.1f}%)")
                
            # Check for SameSite attribute
            if samesite_cookies > 0:
                result['details'].append(f"Cookies with SameSite attribute: {samesite_cookies}")
        else:
            result['details'].append("No cookies detected")
            
        # Check for subresource integrity
        sri_tags = sum(1 for tag in soup.find_all(['script', 'link']) if tag.get('integrity'))
        external_resources = sum(1 for tag in soup.find_all(['script', 'link']) if tag.get('src') or tag.get('href'))
        
        if external_resources > 0:
            sri_percentage = (sri_tags / external_resources) * 100 if external_resources else 0
            
            if sri_percentage >= 50:
                result['score'] += 0.5
                result['details'].append(f"Good use of Subresource Integrity (SRI): {sri_percentage:.1f}%")
            elif sri_tags > 0:
                result['details'].append(f"Some use of Subresource Integrity (SRI): {sri_percentage:.1f}%")
            else:
                result['issues'].append("No Subresource Integrity (SRI) detected")
                
        # Check for mixed content
        if url.startswith('https://'):
            mixed_content_patterns = [
                r'http:\/\/[^"\']*\.(jpg|jpeg|png|gif|css|js)',
                r'src\s*=\s*["\']http:\/\/',
                r'href\s*=\s*["\']http:\/\/'
            ]
            
            has_mixed_content = False
            for pattern in mixed_content_patterns:
                if re.search(pattern, html, re.IGNORECASE):
                    has_mixed_content = True
                    break
                    
            if not has_mixed_content:
                result['score'] += 0.5
                result['details'].append("No mixed content detected")
            else:
                result['issues'].append("Mixed content detected (HTTP resources on HTTPS page)")
                
        return result 

    def check_accessibility(self, url, response, soup, html):
        """
        Check accessibility features of the website.
        
        Args:
            url (str): The URL being analyzed
            response (requests.Response): The response object
            soup (BeautifulSoup): Parsed HTML
            html (str): Raw HTML content
            
        Returns:
            dict: Results of accessibility check with score and details
        """
        logger.info(f"Checking accessibility for {url}")
        result = {
            'score': 0,
            'max_score': 5,
            'details': [],
            'issues': []
        }
        
        # Check for language attribute
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            result['score'] += 0.5
            result['details'].append(f"Language attribute specified: {html_tag.get('lang')}")
        else:
            result['issues'].append("No language attribute specified")
            
        # Check for alt text on images
        img_tags = soup.find_all('img')
        img_with_alt = sum(1 for img in img_tags if img.get('alt') is not None)
        
        if img_tags:
            alt_percentage = (img_with_alt / len(img_tags)) * 100 if img_tags else 0
            
            if alt_percentage == 100:
                result['score'] += 1
                result['details'].append("All images have alt attributes")
            elif alt_percentage >= 80:
                result['score'] += 0.5
                result['details'].append(f"Most images have alt attributes ({alt_percentage:.1f}%)")
            elif alt_percentage > 0:
                result['issues'].append(f"Only {alt_percentage:.1f}% of images have alt attributes")
            else:
                result['issues'].append("No images have alt attributes")
                
        # Check for form labels
        form_controls = soup.find_all(['input', 'select', 'textarea'])
        labeled_controls = 0
        
        for control in form_controls:
            # Skip hidden inputs and submit/button types
            if control.get('type') in ['hidden', 'submit', 'button', 'image']:
                continue
                
            control_id = control.get('id')
            if control_id:
                # Check for label with matching 'for' attribute
                label = soup.find('label', {'for': control_id})
                if label:
                    labeled_controls += 1
                    continue
                    
            # Check for aria-label or aria-labelledby
            if control.get('aria-label') or control.get('aria-labelledby'):
                labeled_controls += 1
                continue
                
            # Check if input is inside a label
            parent_label = control.find_parent('label')
            if parent_label:
                labeled_controls += 1
                
        if form_controls and labeled_controls > 0:
            label_percentage = (labeled_controls / len(form_controls)) * 100
            
            if label_percentage == 100:
                result['score'] += 1
                result['details'].append("All form controls have labels")
            elif label_percentage >= 80:
                result['score'] += 0.5
                result['details'].append(f"Most form controls have labels ({label_percentage:.1f}%)")
            else:
                result['issues'].append(f"Only {label_percentage:.1f}% of form controls have labels")
        elif form_controls:
            result['issues'].append("No form controls have labels")
            
        # Check for ARIA attributes
        elements_with_aria = soup.find_all(lambda tag: any(attr for attr in tag.attrs if attr.startswith('aria-')))
        if elements_with_aria:
            result['score'] += 0.5
            result['details'].append(f"Using ARIA attributes ({len(elements_with_aria)} elements)")
            
        # Check for skip links
        skip_links = soup.find_all('a', href=re.compile(r'^#(content|main|skip)'))
        if skip_links:
            result['score'] += 0.5
            result['details'].append("Skip links detected for keyboard navigation")
        else:
            result['issues'].append("No skip links detected for keyboard navigation")
            
        # Check for sufficient color contrast (basic check)
        # This is a simplified check that looks for very light text on light backgrounds or very dark text on dark backgrounds
        color_contrast_issues = []
        
        # Look for potential contrast issues in inline styles
        light_on_light = re.search(r'color\s*:\s*(#[fF]{3,6}|white|ivory|snow|lightyellow).*background(-color)?\s*:\s*(#[eE-fF]{3,6}|white|ivory|snow|lightyellow)', html)
        dark_on_dark = re.search(r'color\s*:\s*(#[0-3]{3,6}|black|darkblue|darkgreen|darkred).*background(-color)?\s*:\s*(#[0-3]{3,6}|black|darkblue|darkgreen|darkred)', html)
        
        if light_on_light:
            color_contrast_issues.append("Light text on light background detected")
        if dark_on_dark:
            color_contrast_issues.append("Dark text on dark background detected")
            
        if not color_contrast_issues:
            result['score'] += 0.5
            result['details'].append("No obvious color contrast issues detected")
        else:
            result['issues'].extend(color_contrast_issues)
            
        # Check for keyboard navigation support
        keyboard_nav_elements = soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
        elements_with_tabindex = soup.find_all(lambda tag: tag.has_attr('tabindex'))
        
        if elements_with_tabindex:
            result['details'].append(f"Elements with tabindex attribute: {len(elements_with_tabindex)}")
            
            # Check for negative tabindex (removed from tab order)
            negative_tabindex = sum(1 for el in elements_with_tabindex if el.get('tabindex') and int(el.get('tabindex')) < 0)
            if negative_tabindex > 0:
                result['issues'].append(f"{negative_tabindex} elements removed from keyboard tab order")
                
            # Check for tabindex > 0 (custom tab order, generally not recommended)
            custom_tabindex = sum(1 for el in elements_with_tabindex if el.get('tabindex') and int(el.get('tabindex')) > 0)
            if custom_tabindex > 0:
                result['issues'].append(f"{custom_tabindex} elements with custom tab order (tabindex > 0)")
        else:
            result['details'].append("No custom tabindex attributes (using default browser tab order)")
            
        # Check for semantic HTML5 elements
        semantic_elements = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
        semantic_count = sum(1 for element in semantic_elements if soup.find(element))
        
        if semantic_count >= 4:
            result['score'] += 0.5
            result['details'].append(f"Good use of semantic HTML5 elements ({semantic_count}/7)")
        elif semantic_count > 0:
            result['details'].append(f"Some use of semantic HTML5 elements ({semantic_count}/7)")
        else:
            result['issues'].append("No semantic HTML5 elements detected")
            
        # Check for heading structure
        headings = []
        for i in range(1, 7):
            headings.append(len(soup.find_all(f'h{i}')))
            
        if headings[0] > 0:  # Has H1
            # Check for proper heading hierarchy
            proper_hierarchy = True
            for i in range(len(headings) - 1):
                if headings[i] == 0 and headings[i+1] > 0:
                    proper_hierarchy = False
                    break
                    
            if proper_hierarchy:
                result['score'] += 0.5
                result['details'].append("Proper heading hierarchy for screen readers")
            else:
                result['issues'].append("Improper heading hierarchy (skipping levels)")
        else:
            result['issues'].append("No H1 heading found")
            
        return result

    def check_content_quality(self, url, response, soup, html):
        """
        Check content quality and freshness of the website.
        
        Args:
            url (str): The URL being analyzed
            response (requests.Response): The response object
            soup (BeautifulSoup): Parsed HTML
            html (str): Raw HTML content
            
        Returns:
            dict: Results of content quality check with score and details
        """
        logger.info(f"Checking content quality for {url}")
        result = {
            'score': 0,
            'max_score': 5,
            'details': [],
            'issues': []
        }
        
        # Extract all text content
        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'span', 'div'])
        text_content = ' '.join(element.get_text() for element in text_elements)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        # Check content length
        word_count = len(re.findall(r'\b\w+\b', text_content))
        result['details'].append(f"Word count: {word_count}")
        
        if word_count >= 1000:
            result['score'] += 1
            result['details'].append("Substantial content (1000+ words)")
        elif word_count >= 500:
            result['score'] += 0.5
            result['details'].append("Moderate content (500+ words)")
        elif word_count >= 300:
            result['details'].append("Minimal content (300+ words)")
        else:
            result['issues'].append(f"Very little content ({word_count} words)")
            
        # Check for date indicators (content freshness)
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](20\d{2})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(20\d{2})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+(20\d{2})',  # Month DD, YYYY
            r'Updated:?\s+(\d{1,2})[/-](\d{1,2})[/-](20\d{2})',  # Updated: MM/DD/YYYY
            r'Published:?\s+(\d{1,2})[/-](\d{1,2})[/-](20\d{2})',  # Published: MM/DD/YYYY
            r'Posted:?\s+(\d{1,2})[/-](\d{1,2})[/-](20\d{2})',  # Posted: MM/DD/YYYY
            r'Last\s+modified:?\s+(\d{1,2})[/-](\d{1,2})[/-](20\d{2})'  # Last modified: MM/DD/YYYY
        ]
        
        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text_content)
            if matches:
                dates_found.extend(matches)
                
        if dates_found:
            result['score'] += 0.5
            result['details'].append(f"Content contains {len(dates_found)} date references")
            
            # Try to determine if content is recent
            current_year = datetime.now().year
            years_mentioned = re.findall(r'20\d{2}', text_content)
            recent_years = [year for year in years_mentioned if int(year) >= current_year - 2]
            
            if recent_years:
                result['score'] += 0.5
                result['details'].append(f"Content mentions recent years: {', '.join(recent_years)}")
            else:
                result['issues'].append("No recent years mentioned in content")
        else:
            result['issues'].append("No date indicators found (content freshness unknown)")
            
        # Check for social media links
        social_patterns = [
            (r'facebook\.com', 'Facebook'),
            (r'twitter\.com', 'Twitter'),
            (r'linkedin\.com', 'LinkedIn'),
            (r'instagram\.com', 'Instagram'),
            (r'youtube\.com', 'YouTube'),
            (r'pinterest\.com', 'Pinterest'),
            (r'tiktok\.com', 'TikTok')
        ]
        
        social_links = []
        for pattern, name in social_patterns:
            links = soup.find_all('a', href=re.compile(pattern))
            if links:
                social_links.append(name)
                
        if social_links:
            result['score'] += 0.5
            result['details'].append(f"Social media links: {', '.join(social_links)}")
        else:
            result['issues'].append("No social media links found")
            
        # Check for contact information
        contact_patterns = [
            (r'contact', 'Contact page/section'),
            (r'mailto:', 'Email link'),
            (r'tel:', 'Phone link'),
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Email address'),
            (r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,4}', 'Phone number')
        ]
        
        contact_info = []
        for pattern, name in contact_patterns:
            if re.search(pattern, html):
                contact_info.append(name)
                
        if contact_info:
            result['score'] += 0.5
            result['details'].append(f"Contact information: {', '.join(contact_info)}")
        else:
            result['issues'].append("No contact information found")
            
        # Check for multimedia content
        video_elements = soup.find_all(['video', 'iframe'])
        audio_elements = soup.find_all('audio')
        
        if video_elements:
            result['score'] += 0.5
            result['details'].append(f"Video content: {len(video_elements)} elements")
        
        if audio_elements:
            result['score'] += 0.25
            result['details'].append(f"Audio content: {len(audio_elements)} elements")
            
        # Check for interactive elements
        interactive_elements = soup.find_all(['form', 'button', 'select', 'input[type=text]', 'textarea'])
        if interactive_elements:
            result['score'] += 0.5
            result['details'].append(f"Interactive elements: {len(interactive_elements)}")
            
        # Check for blog or news section
        blog_patterns = [r'/blog', r'/news', r'/articles', r'blog\.', r'news\.']
        has_blog = any(re.search(pattern, html) for pattern in blog_patterns)
        
        if has_blog:
            result['score'] += 0.25
            result['details'].append("Blog or news section detected")
            
        return result

    def print_results(self, results):
        """
        Print the analysis results in a formatted way.
        
        Args:
            results (dict): Analysis results for a website
        """
        if results is None:  # Skip printing for 403 errors
            return
            
        if 'error' in results:
            print(f"\n{Fore.RED}Error analyzing {results['url']}: {results['error']}{Style.RESET_ALL}")
            return
            
        print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Website: {results['url']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}OVERALL SCORE: {results['total_score']}/100 ({results['percentage']}%){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Classification: {results['classification']} ({results['lead_potential']}){Style.RESET_ALL}")
        print(f"Analysis completed at: {results['timestamp']}")
        print(f"Initial load time: {results['load_time']:.2f} seconds")
        print(f"Status code: {results['status_code']}")
        
        # Print category scores
        print(f"\n{Fore.GREEN}CATEGORY SCORES:{Style.RESET_ALL}")
        categories = [
            ('SSL Certificate', 'ssl'),
            ('Mobile-Friendliness', 'mobile'),
            ('Page Speed', 'page_speed'),
            ('Technology Stack', 'tech_stack'),
            ('UI Quality', 'ui_quality'),
            ('SEO Optimization', 'seo'),
            ('Security Headers', 'security'),
            ('Accessibility', 'accessibility'),
            ('Content Quality', 'content')
        ]
        
        for name, key in categories:
            category_result = results['categories'][key]
            score_percentage = (category_result['score'] / category_result['max_score']) * 100
            
            # Color-code based on score percentage
            if score_percentage >= 80:
                color = Fore.GREEN
            elif score_percentage >= 50:
                color = Fore.YELLOW
            else:
                color = Fore.RED
                
            print(f"{color}{name}: {category_result['score']}/{category_result['max_score']} ({score_percentage:.1f}%){Style.RESET_ALL}")
            
        # Print details for each category
        for name, key in categories:
            category_result = results['categories'][key]
            
            print(f"\n{Fore.CYAN}{name} Details:{Style.RESET_ALL}")
            
            if category_result['details']:
                for detail in category_result['details']:
                    print(f"  {Fore.GREEN}✓{Style.RESET_ALL} {detail}")
            else:
                print(f"  {Fore.YELLOW}No details available{Style.RESET_ALL}")
                
            if category_result['issues']:
                print(f"\n  {Fore.RED}Issues:{Style.RESET_ALL}")
                for issue in category_result['issues']:
                    print(f"  {Fore.RED}✗{Style.RESET_ALL} {issue}")
                    
        # Print key findings and recommendations
        print(f"\n{Fore.CYAN}KEY FINDINGS:{Style.RESET_ALL}")
        
        # Collect all issues
        all_issues = []
        for key in results['categories']:
            all_issues.extend(results['categories'][key]['issues'])
            
        # Print top 5 issues
        if all_issues:
            for i, issue in enumerate(all_issues[:5]):
                print(f"  {Fore.RED}{i+1}. {issue}{Style.RESET_ALL}")
        else:
            print(f"  {Fore.GREEN}No major issues found{Style.RESET_ALL}")
            
        # Print recommendations based on classification
        print(f"\n{Fore.CYAN}RECOMMENDATIONS:{Style.RESET_ALL}")
        
        if results['classification'] == "Poor":
            print(f"  {Fore.RED}This website urgently needs a complete redesign.{Style.RESET_ALL}")
            print(f"  {Fore.RED}Major issues with security, performance, and user experience.{Style.RESET_ALL}")
        elif results['classification'] == "Outdated":
            print(f"  {Fore.YELLOW}This website needs modernization in several areas.{Style.RESET_ALL}")
            print(f"  {Fore.YELLOW}Consider upgrading the technology stack and improving UX.{Style.RESET_ALL}")
        elif results['classification'] == "Average":
            print(f"  {Fore.YELLOW}This website could benefit from targeted improvements.{Style.RESET_ALL}")
            print(f"  {Fore.YELLOW}Focus on addressing the specific issues identified.{Style.RESET_ALL}")
        elif results['classification'] == "Good":
            print(f"  {Fore.GREEN}This website is performing well but has room for improvement.{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}Consider fine-tuning the areas with lower scores.{Style.RESET_ALL}")
        else:  # Excellent
            print(f"  {Fore.GREEN}This website is performing excellently across most categories.{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}Minor improvements could still be made in specific areas.{Style.RESET_ALL}")
            
        print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
        
    def compare_websites(self, urls):
        """
        Analyze and compare multiple websites.
        
        Args:
            urls (list): List of URLs to analyze and compare
            
        Returns:
            dict: Comparison results
        """
        results = {}
        for url in urls:
            result = self.analyze_website(url)
            if result is not None:  # Only include non-403 results
                results[url] = result
        
        if not results:
            print(f"\n{Fore.RED}No valid results to compare. All websites returned 403 errors.{Style.RESET_ALL}")
            return
        
        comparison = self._generate_comparison(results)
        self._print_comparison(comparison)
        
    def _generate_comparison(self, results):
        """
        Generate comparison data for multiple websites.
        
        Args:
            results (dict): Analysis results for multiple websites
            
        Returns:
            dict: Comparison data
        """
        comparison = {
            'urls': list(results.keys()),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'results': {},
            'summary': {}
        }
        
        # Extract results for each URL
        for url, result in results.items():
            comparison['results'][url] = result
            
        # Calculate average scores for each category
        categories = ['ssl', 'mobile', 'page_speed', 'tech_stack', 'ui_quality', 'seo', 'security', 'accessibility', 'content']
        category_averages = {}
        
        for category in categories:
            scores = [result['categories'][category]['score'] for result in comparison['results'].values() if 'categories' in result]
            max_scores = [result['categories'][category]['max_score'] for result in comparison['results'].values() if 'categories' in result]
            
            if scores and max_scores:
                avg_score = sum(scores) / len(scores)
                avg_max = sum(max_scores) / len(max_scores)
                category_averages[category] = {
                    'avg_score': round(avg_score, 2),
                    'avg_max': round(avg_max, 2),
                    'percentage': round((avg_score / avg_max) * 100, 1) if avg_max > 0 else 0
                }
                
        comparison['summary']['category_averages'] = category_averages
        
        # Calculate overall averages
        total_scores = [result['total_score'] for result in comparison['results'].values()]
        max_scores = [result['max_score'] for result in comparison['results'].values()]
        percentages = [result['percentage'] for result in comparison['results'].values()]
        
        if total_scores and max_scores and percentages:
            comparison['summary']['avg_total_score'] = round(sum(total_scores) / len(total_scores), 1)
            comparison['summary']['avg_max_score'] = round(sum(max_scores) / len(max_scores), 1)
            comparison['summary']['avg_percentage'] = round(sum(percentages) / len(percentages), 1)
            
        # Find best and worst performers
        if percentages:
            best_url = urls[percentages.index(max(percentages))]
            worst_url = urls[percentages.index(min(percentages))]
            
            comparison['summary']['best_performer'] = {
                'url': best_url,
                'score': comparison['results'][best_url]['total_score'],
                'percentage': comparison['results'][best_url]['percentage'],
                'classification': comparison['results'][best_url]['classification']
            }
            
            comparison['summary']['worst_performer'] = {
                'url': worst_url,
                'score': comparison['results'][worst_url]['total_score'],
                'percentage': comparison['results'][worst_url]['percentage'],
                'classification': comparison['results'][worst_url]['classification']
            }
            
        return comparison
        
    def _print_comparison(self, comparison):
        """
        Print the comparison results in a formatted way.
        
        Args:
            comparison (dict): Comparison results
        """
        if not comparison or not comparison.get('results'):
            print(f"\n{Fore.RED}No valid results for comparison{Style.RESET_ALL}")
            return
            
        print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}WEBSITE COMPARISON RESULTS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
        print(f"Comparison completed at: {comparison['timestamp']}")
        print(f"Websites compared: {len(comparison['results'])}")
        
        # Print summary table
        print(f"\n{Fore.YELLOW}OVERALL SCORES:{Style.RESET_ALL}")
        
        headers = ["Website", "Score", "Percentage", "Classification", "Lead Potential"]
        table_data = []
        
        for url, result in comparison['results'].items():
            domain = urlparse(url).netloc
            table_data.append([
                domain,
                f"{result['total_score']}/{result['max_score']}",
                f"{result['percentage']}%",
                result['classification'],
                result['lead_potential']
            ])
            
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Print best and worst performers
        if 'best_performer' in comparison['summary'] and 'worst_performer' in comparison['summary']:
            best = comparison['summary']['best_performer']
            worst = comparison['summary']['worst_performer']
            
            print(f"\n{Fore.GREEN}BEST PERFORMER: {urlparse(best['url']).netloc} ({best['percentage']}%, {best['classification']}){Style.RESET_ALL}")
            print(f"{Fore.RED}WORST PERFORMER: {urlparse(worst['url']).netloc} ({worst['percentage']}%, {worst['classification']}){Style.RESET_ALL}")
            
        # Print category comparison
        print(f"\n{Fore.YELLOW}CATEGORY COMPARISON:{Style.RESET_ALL}")
        
        categories = [
            ('SSL Certificate', 'ssl'),
            ('Mobile-Friendliness', 'mobile'),
            ('Page Speed', 'page_speed'),
            ('Technology Stack', 'tech_stack'),
            ('UI Quality', 'ui_quality'),
            ('SEO Optimization', 'seo'),
            ('Security Headers', 'security'),
            ('Accessibility', 'accessibility'),
            ('Content Quality', 'content')
        ]
        
        category_headers = ["Category"] + [urlparse(url).netloc for url in comparison['results']]
        category_data = []
        
        for name, key in categories:
            row = [name]
            for url in comparison['results']:
                result = comparison['results'][url]
                category_result = result['categories'][key]
                score_percentage = (category_result['score'] / category_result['max_score']) * 100
                row.append(f"{category_result['score']}/{category_result['max_score']} ({score_percentage:.1f}%)")
                
            category_data.append(row)
            
        print(tabulate(category_data, headers=category_headers, tablefmt="grid"))
        
        # Print lead potential summary
        print(f"\n{Fore.YELLOW}LEAD POTENTIAL SUMMARY:{Style.RESET_ALL}")
        
        lead_categories = {
            "High-Priority Lead": [],
            "Potential Lead": [],
            "Maintenance Lead": [],
            "Low-Priority Lead": []
        }
        
        for url, result in comparison['results'].items():
            domain = urlparse(url).netloc
            lead_potential = result['lead_potential']
            lead_categories[lead_potential].append(domain)
            
        for category, domains in lead_categories.items():
            if domains:
                if category == "High-Priority Lead":
                    color = Fore.RED
                elif category == "Potential Lead":
                    color = Fore.YELLOW
                elif category == "Maintenance Lead":
                    color = Fore.BLUE
                else:
                    color = Fore.GREEN
                    
                print(f"{color}{category}: {', '.join(domains)}{Style.RESET_ALL}")
                
        print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
        
def main():
    """Main function to run the website grader."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Website Grader - Analyze and score websites')
    parser.add_argument('urls', nargs='+', help='URLs to analyze')
    parser.add_argument('--timeout', type=int, default=20, help='Request timeout in seconds')
    parser.add_argument('--retries', type=int, default=2, help='Maximum retry attempts')
    parser.add_argument('--output', help='Output file for results (JSON format)')
    parser.add_argument('--compare', action='store_true', help='Compare multiple websites')
    
    args = parser.parse_args()
    
    try:
        # Initialize the grader
        grader = WebsiteGraderV4(timeout=args.timeout, max_retries=args.retries)
        
        if args.compare and len(args.urls) > 1:
            # Compare multiple websites
            comparison = grader.compare_websites(args.urls)
            
            # Save results to file if specified
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(comparison, f, indent=2)
                print(f"\nComparison results saved to {args.output}")
        else:
            # Analyze a single website
            for url in args.urls:
                result = grader.analyze_website(url)
                grader.print_results(result)
                
            # Save results to file if specified
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(grader.results, f, indent=2)
                print(f"\nAnalysis results saved to {args.output}")
                
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        return 1
        
    return 0
    
if __name__ == "__main__":
    sys.exit(main())
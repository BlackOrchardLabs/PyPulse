"""
PyPulse Example: Web Scraping with Progress Tracking
Demonstrates using PyPulse for web scraping tasks
"""

import time
import random
from urllib.parse import urljoin
from pypulse import pulse_progress, pulse_task

def simulate_web_scraping():
    """Simulate a web scraping workflow"""
    
    print("Starting web scraping workflow...")
    
    # Simulate website structure
    base_url = "https://example-shop.com"
    categories = [
        "electronics",
        "books", 
        "clothing",
        "home-garden",
        "sports"
    ]
    
    with pulse_task("Web Scraping Workflow", total_steps=5) as task:
        
        # Step 1: Discover categories
        task.step("Discovering product categories", progress=0.1)
        discovered_urls = []
        
        for category in pulse_progress(categories, 
                                      task="Scanning categories", 
                                      step="1/5"):
            time.sleep(0.5)  # Simulate page load
            
            # Simulate finding product URLs
            num_products = random.randint(20, 50)
            for i in range(num_products):
                product_url = f"{base_url}/{category}/product_{i+1}"
                discovered_urls.append(product_url)
        
        # Step 2: Fetch product pages
        task.step("Fetching product pages", progress=0.3)
        product_data = []
        
        # Process URLs in batches
        batch_size = 10
        num_batches = len(discovered_urls) // batch_size + 1
        
        for batch_num in pulse_progress(range(num_batches), 
                                       task="Fetching batches", 
                                       step="2/5"):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(discovered_urls))
            batch_urls = discovered_urls[start_idx:end_idx]
            
            # Simulate fetching each URL
            for url in batch_urls:
                time.sleep(random.uniform(0.1, 0.3))  # Simulate network delay
                
                # Simulate scraping data
                product_data.append({
                    "url": url,
                    "title": f"Product {len(product_data) + 1}",
                    "price": round(random.uniform(10.0, 500.0), 2),
                    "rating": round(random.uniform(3.0, 5.0), 1),
                    "reviews": random.randint(0, 1000)
                })
        
        # Step 3: Clean and validate data
        task.step("Cleaning scraped data", progress=0.5)
        cleaned_data = []
        
        for product in pulse_progress(product_data, 
                                     task="Data cleaning", 
                                     step="3/5"):
            time.sleep(0.02)  # Simulate processing
            
            # Simulate data validation
            if product["price"] > 0 and product["rating"] >= 3.0:
                # Add computed fields
                product["price_category"] = "High" if product["price"] > 100 else "Low"
                product["popularity_score"] = product["reviews"] * product["rating"]
                cleaned_data.append(product)
        
        # Step 4: Analyze data
        task.step("Analyzing scraped data", progress=0.7)
        
        # Simulate various analyses
        analyses = [
            "Price distribution analysis",
            "Rating pattern detection", 
            "Review sentiment analysis",
            "Category performance metrics"
        ]
        
        analysis_results = {}
        for analysis in pulse_progress(analyses, 
                                      task="Running analyses", 
                                      step="4/5"):
            time.sleep(random.uniform(0.5, 1.5))
            
            # Simulate analysis results
            if "price" in analysis.lower():
                avg_price = sum(p["price"] for p in cleaned_data) / len(cleaned_data)
                analysis_results["avg_price"] = round(avg_price, 2)
            elif "rating" in analysis.lower():
                avg_rating = sum(p["rating"] for p in cleaned_data) / len(cleaned_data)
                analysis_results["avg_rating"] = round(avg_rating, 2)
            elif "sentiment" in analysis.lower():
                positive_ratio = random.uniform(0.6, 0.9)
                analysis_results["positive_reviews"] = round(positive_ratio, 2)
            else:
                analysis_results["category_performance"] = "completed"
        
        # Step 5: Generate report
        task.step("Generating analysis report", progress=0.9)
        
        # Simulate report generation
        report_sections = [
            "Executive Summary",
            "Data Collection Summary", 
            "Key Findings",
            "Statistical Analysis",
            "Recommendations",
            "Appendix"
        ]
        
        for section in pulse_progress(report_sections, 
                                     task="Writing report sections", 
                                     step="5/5"):
            time.sleep(0.3)
        
        # Final update
        task.step("Scraping complete!", progress=1.0)
        time.sleep(0.5)
    
    # Print summary
    print("\n" + "="*60)
    print("WEB SCRAPING SUMMARY")
    print("="*60)
    print(f"Total URLs discovered: {len(discovered_urls)}")
    print(f"Products successfully scraped: {len(cleaned_data)}")
    print(f"Data quality: {len(cleaned_data)/len(product_data)*100:.1f}%")
    print("\nAnalysis Results:")
    for key, value in analysis_results.items():
        print(f"  {key}: {value}")
    print(f"\nReport generated with {len(report_sections)} sections")
    print("="*60)

def simulate_api_monitoring():
    """Simulate monitoring multiple API endpoints"""
    
    print("\nStarting API monitoring simulation...")
    
    api_endpoints = [
        "/api/v1/products",
        "/api/v1/users", 
        "/api/v1/orders",
        "/api/v1/analytics",
        "/api/v1/notifications"
    ]
    
    # Monitor each endpoint
    for endpoint in pulse_progress(api_endpoints, task="API Health Check"):
        time.sleep(0.5)  # Simulate API call
        
        # Simulate response time and status
        response_time = random.uniform(0.1, 2.0)
        status_code = random.choice([200, 200, 200, 200, 429, 500])  # Mostly successful
        
        if status_code == 200:
            print(f"  ✓ {endpoint}: {response_time:.2f}s")
        else:
            print(f"  ✗ {endpoint}: HTTP {status_code}")
    
    print("API monitoring complete!")

if __name__ == "__main__":
    # Run the web scraping simulation
    simulate_web_scraping()
    
    # Run API monitoring
    simulate_api_monitoring()
    
    print("\nAll simulations completed successfully!")
    print("This demonstrates how PyPulse can track complex workflows with multiple progress levels.")
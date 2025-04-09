import scrapy


class UniversityListSpider(scrapy.Spider):
    name = "university_list"
    allowed_domains = ["www.4icu.org"]
    start_urls = ["https://www.4icu.org/in/a-z/"]

    def parse(self, response):
        for row in response.css('table.table-hover tbody tr'):
            rank = row.css('td:nth-child(1) b::text').get()
            university = row.css('td:nth-child(2) a::text').get()
            town = row.css('td:nth-child(3)::text').get()
            university_link = row.css('td:nth-child(2) a::attr(href)').get()
            
            university_url = response.urljoin(university_link)
            
            yield scrapy.Request(
                url=university_url,
                callback=self.parse_university,
                meta={
                    'rank': rank.strip() if rank else 'N/A',
                    'university': university.strip() if university else 'N/A',
                    'town': town.strip() if town else 'N/A'
                }
            )
            
    def parse_university(self, response):
        rank = response.meta['rank']
        university = response.meta['university']
        town = response.meta['town']  
        
        overview = response.css('div.panel-heading h2::text').get()
        if overview and overview.strip() == 'Overview':
            overview_text = response.css('div.panel-body p[itemprop="description"]::text').get()      
            
        university_identity = {
            'name': response.css("th:contains('Name ') + td span[itemprop='name'] strong::text").get(),
            'non_latin_name': response.css("th:contains('Name (Non Latin)') + td span[itemprop='alternateName'] strong::text").get(),
            'acronym': response.css("th:contains('Acronym ') + td abbr strong::text").get(),
            'founded': response.css("th:contains('Founded ') + td span[itemprop='foundingDate'] strong::text").get(),
            'website': response.css("th:contains('Name ') + td a::attr(href)").get(),
            'screenshot': response.css("th:contains('Screenshot ') + td a img::attr(src)").get(),
        }
        
        university_location = {
            'street_address': response.css("span[itemprop='streetAddress']::text").get(),
            'locality': response.css("span[itemprop='addressLocality']::text").get(),
            'postal_code': response.css("span[itemprop='postalCode']::text").get(),
            'region': response.css("span[itemprop='addressRegion']::text").get(),
            'country': 'India',
            'phone_number': response.css("img[alt*='Phone Number'] + td::text").get(),
            'fax_number': response.css("img[alt*='Fax Number'] + td::text").get(),
            'location_map': response.css("a[href*='maps']::attr(href)").get(),
        }  
        
        additional_info = {
                'name': response.css("h1[itemprop='name']::text").get(),
                'logo': response.css("img[itemprop='logo']::attr(src)").get(),
                'country_rank': response.css("a[href*='/in/'] span[style*='font-weight:bold']::text").get(),
                'world_rank': response.css("a[href*='/reviews/'] span[style*='font-weight:bold']::text").get(),
                'details_link': response.urljoin(response.css("a[itemprop='url']::attr(href)").get()),
        } 
        
        yield{
            'Rank': rank,
            'University': university,
            'Town': town,
            'additional_info': additional_info,
            'overview': overview_text,
            'university_identity': university_identity,
            'university_location': university_location
        }

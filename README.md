# Podcast Organizer

Take an ompl file from a podcast app (like iCatcher) and organize all the subscriptions.

This tool will get all rss feeds from an ompl file and pull the podcast information and format it into a nice markdown file. For example the podcast How I AI from the ompl file should have output that looks like this.

Short Example

Source:

```
<outline type="rss" text="How%20I%20AI" title="How%20I%20AI" xmlUrl="https://anchor.fm/s/1035b1568/podcast/rss"  <kbd></kbd>

```

Desired Output:

# AI Podcasts

Title: How I AI
Link: [rss](https://anchor.fm/s/1035b1568/podcast/rss)
YouTube Link: [How I AI - YouTube](https://www.youtube.com/@howiaipodcast)
Description: 
How I AI, hosted by Claire Vo, is for anyone wondering how to actually use these magical new tools to improve the quality and efficiency of their work. In each episode, guests will share a specific, practical, and impactful way they’ve learned to use AI in their work or life. Expect 30-minute episodes, live screen sharing, and tips/tricks/workflows you can copy immediately. If you want to demystify AI and learn the skills you need to thrive in this new world, this podcast is for you.

Tags: #ai #productmanagement ...

To create this there will be several steps.

Step 1: get RSS feed info
Step 2: turn into markdown formatted file
Step 3: Enrich with tags and other info using AI

# Step 1: get RSS feed info

Read the OMPL file and for each outline  entry pull out the text, title, and url.

Example entry.
```
<outline type="rss" text="How%20I%20AI" title="How%20I%20AI" xmlUrl="https://anchor.fm/s/1035b1568/podcast/rss"  <kbd></kbd>
```

For each rss url get the content of the url via curl or similar. It should be a well formatted rss xml feed. In the <channel> section of the feed you can pull all the podcast details. 

# Step 2: turn into markdown formatted file

Take all the rss feeds and pullFrom that section pull the following and put into the final podcast list file.  The info to pull includes

- title
- link
- description
- image link

Example snippet from rss xml feed.

```
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:googleplay="http://www.google.com/schemas/play-podcasts/1.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/" xmlns:content="http://purl.org/rss/1.0/modules/content/" version="2.0">
<channel>
<atom:link href="https://feeds.megaphone.fm/TNM5447738590" rel="self" type="application/rss+xml"/>
<title>Inspire To FIRE Podcast (Financial Independence Retire Early)</title>
<link>https://www.inspiretofire.com</link>
<language>en</language>
<copyright>Mr. Inspire To FIRE</copyright>
<description>A show dedicated to providing you with inspirational content for Financial Independence Retire Early (FIRE). Easy and Actionable tips with all the resources you need to crush your FIRE goals! On the show, we interview amazing guests from the business and finance world. We explore personal finance topics, investing strategies, and wealth-building ideas. To be part of the show or ask a question send me an email at questions@inspiretofire.com</description>
<image>
<url>https://megaphone.imgix.net/podcasts/8dbcd548-ba85-11ec-8b90-af161de4c359/image/4231002-1636652166640-fcbe8770dc406.jpg?ixlib=rails-4.3.1&max-w=3000&max-h=3000&fit=crop&auto=format,compress</url>
<title>Inspire To FIRE Podcast (Financial Independence Retire Early)</title>
<link>https://www.inspiretofire.com</link>
</image>
<itunes:explicit>yes</itunes:explicit>
<itunes:type>episodic</itunes:type>
<itunes:subtitle/>
<itunes:author>Mr. Inspire To FIRE</itunes:author>
<itunes:summary>A show dedicated to providing you with inspirational content for Financial Independence Retire Early (FIRE). Easy and Actionable tips with all the resources you need to crush your FIRE goals! On the show, we interview amazing guests from the business and finance world. We explore personal finance topics, investing strategies, and wealth-building ideas. To be part of the show or ask a question send me an email at questions@inspiretofire.com</itunes:summary>
<content:encoded>
<![CDATA[ A show dedicated to providing you with inspirational content for Financial Independence Retire Early (FIRE). Easy and Actionable tips with all the resources you need to crush your FIRE goals! On the show, we interview amazing guests from the business and finance world. We explore personal finance topics, investing strategies, and wealth-building ideas. To be part of the show or ask a question send me an email at questions@inspiretofire.com ]]>
</content:encoded>
<itunes:owner>
<itunes:name>Mr. Inspire To FIRE</itunes:name>
<itunes:email>Questions@inspiretofire.com</itunes:email>
</itunes:owner>
<itunes:image href="https://megaphone.imgix.net/podcasts/8dbcd548-ba85-11ec-8b90-af161de4c359/image/4231002-1636652166640-fcbe8770dc406.jpg?ixlib=rails-4.3.1&max-w=3000&max-h=3000&fit=crop&auto=format,compress"/>
<itunes:category text="Business">
<itunes:category text="Entrepreneurship"/>
</itunes:category>
<item>
<title>Retiring Early As A Couple - With Greg and Maggie</title>
<link>https://www.inspiretofire.com/</link>
<description>I talk to Greg and Maggie about their recent early retirement. Sponsor: Magic Mind Go to https://www.magicmind.co/inspiretofire And get up to 56% off your subscription for the next 10 days with my code INSPIRETOFIRE. Please Subscribe & Leave A Review More Resources Friends On FIRE Podcast Track Your Expenses With Personal Capital Save Money On Your Phone Bill With Mint Mobile Save Money On Prescriptions With GoodRx Earn Travel Points With Delta SkyMiles Card Money Affirmations Find More Episodes At InspiretoFIRE.com/Podcast These notes may contain affiliate links, meaning I receive commissions if you purchase through the links I provide (at no extra cost). Thank you for supporting my work! Disclaimer: This is not tax, investment, or financial advice. This is a podcast meant to entertain. None of what is said should be taken as financial advice. Please consult your advisors regarding your matters. Learn more about your ad choices. Visit megaphone.fm/adchoices</description>
<pubDate>Tue, 02 May 2023 10:00:00 -0000</pubDate>
<itunes:title>Retiring Early As A Couple - With Greg and Maggie</itunes:title>
<itunes:episodeType>full</itunes:episodeType>
<itunes:season>2</itunes:season>
<itunes:episode>11</itunes:episode>
<itunes:author>Mr. Inspire To FIRE</itunes:author>
<itunes:subtitle>Retiring Early As A Couple - With Greg and Maggie</itunes:subtitle>
<itunes:summary>I talk to Greg and Maggie about their recent early retirement. Sponsor: Magic Mind Go to https://www.magicmind.co/inspiretofire And get up to 56% off your subscription for the next 10 days with my code INSPIRETOFIRE. Please Subscribe & Leave A Review More Resources Friends On FIRE Podcast Track Your Expenses With Personal Capital Save Money On Your Phone Bill With Mint Mobile Save Money On Prescriptions With GoodRx Earn Travel Points With Delta SkyMiles Card Money Affirmations Find More Episodes At InspiretoFIRE.com/Podcast These notes may contain affiliate links, meaning I receive commissions if you purchase through the links I provide (at no extra cost). Thank you for supporting my work! Disclaimer: This is not tax, investment, or financial advice. This is a podcast meant to entertain. None of what is said should be taken as financial advice. Please consult your advisors regarding your matters. Learn more about your ad choices. Visit megaphone.fm/adchoices</itunes:summary>
<content:encoded>
<![CDATA[ <p>I talk to Greg and Maggie about their recent early retirement.</p><p><br></p><p><strong>Sponsor: Magic Mind</strong></p><p><em>Go to </em><a href="https://www.magicmind.co/inspiretofire"><em>https://www.magicmind.co/inspiretofire</em></a><em> And get up to 56% off your subscription for the next 10 days with my code </em><strong><em>INSPIRETOFIRE</em></strong><em>.</em></p><p><br></p><p><strong>Please Subscribe &amp; Leave A Review</strong></p><p><br></p><p><strong>More Resources</strong></p><p><a href="https://podcasts.apple.com/us/podcast/friends-on-fire/id1491570606">Friends On FIRE Podcast</a></p><p><a href="https://www.inspiretofire.com/PersonalCapital">Track Your Expenses With Personal Capital</a></p><p><a href="https://mint-mobile.58dp.net/MXPD52">Save Money On Your Phone Bill With Mint Mobile</a></p><p><a href="https://www.goodrx.com/">Save Money On Prescriptions With GoodRx</a></p><p><a href="https://www.americanexpress.com/en-us/credit-cards/referral/prospect/cards/business/CHRISE6G4m?CORID=C~H~R~I~S~E~6~G~4~m-1678798689983-1699850538&amp;GENCODE=349992927484970&amp;XL=MNDEM&amp;cellid=&amp;cellid=&amp;extlink=US-MGM-MOBN_DEEPLINK-email-756-205937-GG1R%3A0001">Earn Travel Points With Delta SkyMiles Card</a></p><p><a href="https://www.inspiretofire.com/money-affirmations/">Money Affirmations</a></p><p><br></p><p>Find More Episodes At <a href="https://www.inspiretofire.com/podcast/">InspiretoFIRE.com/Podcast</a></p><p><em>These notes may contain affiliate links, meaning I receive commissions if you purchase through the links I provide (at no extra cost).</em></p><p><em>Thank you for supporting my work!</em></p><p><br></p><p><strong><em>Disclaimer</em></strong><em>: This is not tax, investment, or financial advice. This is a podcast meant to entertain. None of what is said should be taken as financial advice. Please consult your advisors regarding your matters.</em></p><p> </p><p>Learn more about your ad choices. Visit <a href="https://megaphone.fm/adchoices">megaphone.fm/adchoices</a></p> ]]>
</content:encoded>
<itunes:duration>3540</itunes:duration>
<guid isPermaLink="false">
<![CDATA[ c4b11fbe-e5ef-11ed-a202-3fbeeae1e612 ]]>
</guid>
<enclosure url="https://traffic.megaphone.fm/TNM1005521161.mp3?updated=1682710561" length="0" type="audio/mpeg"/>
</item>
```




# Step 3: Enrich with tags and other info using AI

Use AI to organize the podcasts into a markdown file formatted as follows.

## Podcasts organizer prompt

Read my OMPL list of my subscribers podcasts and create a markdown file appropriate for obsidian containing all my podcasts categorized by major theme.

For each entry include the podcast name, podcast url, and a series of tags.

For each look up better reference links for each podcast. Ideally find a link to the YouTube version of the podcast as well. Add a short description of the podcast as well which you might get from YouTube or another site.

  Short Example

Source:

```
<outline type="rss" text="How%20I%20AI" title="How%20I%20AI" xmlUrl="https://anchor.fm/s/1035b1568/podcast/rss"  <kbd></kbd>

```

Desired Output:

# AI Podcasts

Title: How I AI
Link: [rss](https://anchor.fm/s/1035b1568/podcast/rss)
YouTube Link: [How I AI - YouTube](https://www.youtube.com/@howiaipodcast)
Description: 
How I AI, hosted by Claire Vo, is for anyone wondering how to actually use these magical new tools to improve the quality and efficiency of their work. In each episode, guests will share a specific, practical, and impactful way they’ve learned to use AI in their work or life. Expect 30-minute episodes, live screen sharing, and tips/tricks/workflows you can copy immediately. If you want to demystify AI and learn the skills you need to thrive in this new world, this podcast is for you.

Tags: #ai #productmanagement ...

# Retirement Podcasts

...


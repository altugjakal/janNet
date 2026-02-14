from managers.model_manager import get_model
from utils.parsing import html_to_clean

model = get_model()
html = '''<!DOCTYPE html>
  <html lang="en" dir="ltr" prefix="og: https://ogp.me/ns#" class="no-js">
  <head>
    <meta charset="utf-8" />
<script async src="https://www.googletagmanager.com/gtag/js?id=G-RJLQH43QXH"></script>
<script>window.dataLayer = window.dataLayer || [];function gtag(){dataLayer.push(arguments)};gtag("js", new Date());gtag("set", "developer_id.dMDhkMT", true);gtag("config", "G-RJLQH43QXH", {"groups":"default","page_placeholder":"PLACEHOLDER_page_location","allow_ad_personalization_signals":false,"cookie_domain":"www.cs.stanford.edu","cookie_prefix":"su","cookie_expires":15552000});</script>
<link rel="canonical" href="https://www.cs.stanford.edu/about/gates-computer-science-building" />
<meta property="og:site_name" content="Computer Science" />
<meta property="og:type" content="website" />
<meta property="og:url" content="https://www.cs.stanford.edu/about/gates-computer-science-building" />
<meta property="og:title" content="Gates Computer Science Building" />
<meta property="og:image" content="https://www.cs.stanford.edu/sites/g/files/sbiybj28076/files/styles/card_1192x596/public/media/image/gates-builing_topbanner_clouds_0.jpg?h=d41eb344&amp;itok=_52hnTi7" />
<meta property="og:image:url" content="https://www.cs.stanford.edu/sites/g/files/sbiybj28076/files/styles/card_1192x596/public/media/image/gates-builing_topbanner_clouds_0.jpg?h=d41eb344&amp;itok=_52hnTi7" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Gates Computer Science Building" />
<meta name="twitter:image" content="https://www.cs.stanford.edu/sites/g/files/sbiybj28076/files/styles/card_1192x596/public/media/image/gates-builing_topbanner_clouds_0.jpg?h=d41eb344&amp;itok=_52hnTi7" />
<meta name="Generator" content="Drupal 11 (https://www.drupal.org)" />
<meta name="MobileOptimized" content="width" />
<meta name="HandheldFriendly" content="true" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<link rel="icon" href="/profiles/custom/soe_profile/themes/soe_basic/favicon.ico" type="image/vnd.microsoft.icon" />
    <title>Gates Computer Science Building | Computer Science</title>
</head>
<body class="sws-acsf page-about-gates-computer-science-building section-about not-front role--anonymous">
<div class="dialog-off-canvas-main-canvas" data-off-canvas-main-canvas>
<header class="su-masthead su-masthead--right" data-nosnippet>
<a href="#main-content" class="visually-hidden focusable su-skipnav su-skipnav--content">Skip to main content</a>
<nav class="su-multi-menu--dropdowns su-multi-menu su-multi-menu--buttons su-multi-menu--right no-js" aria-label="main menu">
<button class="su-multi-menu__nav-toggle su-multi-menu__nav-toggle--right " aria-expanded="false">Menu</button>
<ul class="su-multi-menu__menu su-multi-menu__menu-lv1"><li class="su-multi-menu__item"><a class="su-multi-menu__link" href="/home"><span class="su-multi-menu__link-text-wrapper">Home</span></a></li><li class="su-multi-menu__item"><a class="su-multi-menu__link" href="/about"><span class="su-multi-menu__link-text-wrapper">About</span></a></li></ul>
</nav>
</header>
<main class="page-content" id="page-content">
<section class="node--stanford-page node-page--stanford-page node basic-page node--layout-full">
<div class="content">
<div class="node stanford-page title string label-hidden"><h1>Gates Computer Science Building</h1></div>
<div class="su-wysiwyg-text paragraph stanford-wysiwyg text-long label-hidden"><h2>Designed to Foster Interaction</h2><p>The Gates Building is named for Bill Gates, co-founder and CEO of Microsoft Corp., who gave a $6 million gift to the project. It was completed in January 1996 and is the home of the Computer Science Department. The 150,000-square-foot building houses 550 faculty, staff, and students and cost $38M to build and furnish. Robert A. M. Stern Associates of New York and Fong and Chan of San Francisco were the architects, selected following an invited national competition. Rudolph &amp; Sletten of Foster City was the general contractor. There were 47 subcontractors working over a 16-month period.</p></div>
<div class="su-wysiwyg-text paragraph stanford-wysiwyg text-long label-hidden"><p class="su-intro-text">The Gates Building was designed to promote interaction.</p></div>
<div class="su-wysiwyg-text paragraph stanford-wysiwyg text-long label-hidden"><p>The Gates Building offers two new state-of-the-art classrooms which are equipped with computer presentation tools and equipment, large screen projectors, and accommodation for multiple computer platforms.</p></div>
<div class="su-wysiwyg-text paragraph stanford-wysiwyg text-long label-hidden"><p>A coalition of Stanford computer scientists and the <a href="http://www.computerhistory.org/">Computer History Museum</a> has installed exhibits within the Gates Computer Science building containing historical equipment and documents focusing on Stanford\'s role in the history of computing.</p></div>
</div>
</section>
</main>
<footer id="footer" data-nosnippet>
<div class="su-global-footer">
<span>&copy; Stanford University.</span>
<span>Stanford, California 94305.</span>
</div>
</footer>
</div>
</body>
</html>'''
html = html_to_clean(html)

print(model.encode(html) @ model.encode("Gates Computer Science Building"))

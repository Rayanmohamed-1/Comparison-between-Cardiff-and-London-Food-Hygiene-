SELECT
    location,
    COUNT(*) AS total_establishments
FROM establishments
GROUP BY location;

SELECT
    location,
    rating,
    COUNT(*) AS establishment_count
FROM establishments
GROUP BY location, rating
ORDER BY location, rating DESC;

SELECT
    location,
    ROUND(AVG(rating), 2) AS average_rating,
    COUNT(rating) AS rated_establishments
FROM establishments
GROUP BY location;

SELECT
    location,
    COUNT(rating) AS rated_establishments,
    SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END)
        AS five_star_establishments,
    ROUND(
        100.0 * SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(rating), 0),
        2
    ) AS five_star_percentage
FROM establishments
GROUP BY location;

SELECT
    location,
    business_type,
    COUNT(rating) AS rated_establishments,
    ROUND(AVG(rating), 2) AS average_rating
FROM establishments
WHERE rating IS NOT NULL
GROUP BY location, business_type
HAVING COUNT(rating) >= 10
ORDER BY average_rating ASC;

SELECT
    location,
    ROUND(AVG(hygiene), 2) AS avg_hygiene_score,
    ROUND(AVG(structural), 2) AS avg_structural_score,
    ROUND(AVG(management), 2) AS avg_management_score
FROM establishments
GROUP BY location;


-- name: total_establishments
SELECT
    city,
    COUNT(*) AS total_establishments
FROM establishments
GROUP BY city;

-- name: rating_status_by_city
SELECT
    city,
    rating_status,
    COUNT(*) AS establishments,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY city), 2)
        AS pct_of_city
FROM establishments
GROUP BY city, rating_status
ORDER BY city, establishments DESC;

-- name: rating_distribution
SELECT
    city,
    rating,
    COUNT(*) AS establishments,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY city), 2)
        AS pct_of_rated
FROM establishments
WHERE rating IS NOT NULL
GROUP BY city, rating
ORDER BY city, rating DESC;

-- name: average_rating_and_five_star
SELECT
    city,
    COUNT(rating) AS rated_establishments,
    ROUND(AVG(rating), 2) AS average_rating,
    ROUND(
        100.0 * SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(rating), 0),
        2
    ) AS five_star_pct
FROM establishments
GROUP BY city;

-- name: ratings_by_business_type
SELECT
    city,
    business_type,
    COUNT(rating) AS rated_establishments,
    ROUND(AVG(rating), 2) AS average_rating
FROM establishments
WHERE rating IS NOT NULL
GROUP BY city, business_type
HAVING COUNT(rating) >= 10
ORDER BY business_type, city;

-- name: component_scores_by_rating
SELECT
    rating,
    COUNT(*) AS establishments,
    ROUND(AVG(hygiene_score), 2) AS avg_hygiene_score,
    ROUND(AVG(structural_score), 2) AS avg_structural_score,
    ROUND(AVG(management_score), 2) AS avg_management_score
FROM establishments
WHERE rating IS NOT NULL
GROUP BY rating
ORDER BY rating DESC;

-- name: component_scores_by_city
SELECT
    city,
    ROUND(AVG(hygiene_score), 2) AS avg_hygiene_score,
    ROUND(AVG(structural_score), 2) AS avg_structural_score,
    ROUND(AVG(management_score), 2) AS avg_management_score
FROM establishments
WHERE rating IS NOT NULL
GROUP BY city;

-- name: inspection_recency
SELECT
    city,
    rating,
    COUNT(*) AS establishments,
    ROUND(AVG(days_since_inspection) / 365.0, 1) AS avg_years_since_inspection
FROM establishments
WHERE rating IS NOT NULL
GROUP BY city, rating
ORDER BY city, rating DESC;

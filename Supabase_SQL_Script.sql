drop table if exists fact_environmental_conditions;

create table fact_environmental_conditions (
    fact_id bigint generated always as identity primary key,
    datetime_id bigint,
    env_id int,
    temperature_2m double precision,
    wind_speed_10m double precision,
    precipitation_proabability double precision,
    soil_temperature_0cm double precision,
    soil_moisture_0_to_1cm double precision,
    pm25 double precision,
    ozone double precision,
    us_aqi int,
    grass_pollen double precision,
    ragweed_pollen double precision,
    birch_pollen double precision,
    alder_pollen double precision,
    mugwort_pollen double precision,
    olive_pollen double precision,
    planting_readiness boolean,
    allergy_risk boolean,
    high_wind_flag boolean,
    rain_expected_flag boolean,
    soil_too_wet_flag boolean,
    poor_air_quality_flag boolean,
    high_pollen_flag boolean
);

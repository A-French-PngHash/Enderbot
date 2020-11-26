DROP TABLE IF EXISTS Tools;
DROP TABLE IF EXISTS Resources;
DROP TABLE IF EXISTS Village;
DROP TABLE IF EXISTS Treasures;
DROP TABLE IF EXISTS Player;
DROP TABLE IF EXISTS Tower;
DROP TABLE IF EXISTS Tower_bosses;
DROP TABLE IF EXISTS ResourcesDropped;


CREATE TABLE Player (
	id BIGINT NOT NULL,  
	tools_id MEDIUMINT NOT NULL,
	mana FLOAT NOT NULL,
	xp INT NOT NULL,
	life_points FLOAT NOT NULL,
	energy FLOAT NOT NULL,
	resource_id MEDIUMINT NOT NULL,
	last_lookup DATETIME NOT NULL,
	actual_shard_id TINYINT NOT NULL,
	treasure_combo TINYINT NOT NULL,
	inventory_color BINARY(3) NOT NULL,
	last_daily_claim DATETIME,
	last_hourly_claim DATETIME,
	hourly_combo TINYINT NOT NULL,
	reputations MEDIUMINT NOT NULL,
	last_reputation_claim DATETIME,
	village_id MEDIUMINT NOT NULL,
	tower_id MEDIUMINT NOT NULL,
	orbs BIGINT NOT NULL,
	PRIMARY KEY(id)
)
ENGINE=INNODB;

CREATE TABLE Tools (
	id MEDIUMINT NOT NULL AUTO_INCREMENT,
	pickaxe_level TINYINT NOT NULL,
	house_level TINYINT NOT NULL,
	ring_level TINYINT NOT NULL,
	sword_level TINYINT NOT NULL,
	shield_level TINYINT NOT NULL,
	PRIMARY KEY (id)
)
ENGINE=INNODB;

CREATE TABLE Resources (
	id MEDIUMINT NOT NULL AUTO_INCREMENT,
	pp INT NOT NULL,
	am INT NOT NULL,
	stone BIGINT NOT NULL,
	iron BIGINT NOT NULL,
	gold BIGINT NOT NULL,
	obsidian BIGINT NOT NULL,
	ruby BIGINT NOT NULL,
	emerald BIGINT NOT NULL,
	sapphire BIGINT NOT NULL,
	cobalt BIGINT NOT NULL,
	adamantite BIGINT NOT NULL,
	mithril BIGINT NOT NULL,
	PRIMARY KEY (id)
)
ENGINE=INNODB;

CREATE TABLE Village(
    id MEDIUMINT NOT NULL AUTO_INCREMENT,
    stone_inside BIGINT NOT NULL,
    last_lookup DATETIME,
    last_claim DATETIME,
    factories INT NOT NULL,
    academies INT NOT NULL,
    inhabitants INT NOT NULL,
    PRIMARY KEY (id)
)
ENGINE=INNODB;

CREATE TABLE Tower(
    id MEDIUMINT NOT NULL AUTO_INCREMENT,
    floor TINYINT NOT NULL,
    pos_x TINYINT NOT NULL,
    pos_y TINYINT NOT NULL
    PRIMARY KEY (id)
)
ENGINE=INNODB;

CREATE TABLE ResourcesDropped(
    channel_id BIGINT NOT NULL,
    dropper_id BIGINT NOT NULL,
    resources_id MEDIUMINT NOT NULL
)
ENGINE=INNODB;


CREATE TABLE Treasures (
    shard TINYINT NOT NULL,
    release_date DATETIME NOT NULL,
    last_person_id BIGINT NOT NULL,
    last_guild_id BIGINT NOT NULL,
    PRIMARY KEY (shard)
)
ENGINE=INNODB;

CREATE TABLE NumberOfTimeFoughtBoss(
    id MEDIUMINT NOT NULL AUTO_INCREMENT,
    
)


ALTER TABLE Player
ADD UNIQUE ind_resource_id (resource_id);

ALTER TABLE Player
ADD CONSTRAINT fk_resource_id_id FOREIGN KEY (resource_id) REFERENCES Resources(id);

ALTER TABLE Player
ADD UNIQUE ind_tools_id (tools_id);

ALTER TABLE Player
ADD CONSTRAINT fk_tools_id_id FOREIGN KEY (tools_id) REFERENCES Tools(id);

ALTER TABLE Player
ADD CONSTRAINT fk_village_id_id FOREIGN KEY (village_id) REFERENCES Village(id);

ALTER TABLE Player
ADD CONSTRAINT fk_tower_id_id FOREIGN KEY (tower_id) REFERENCES Tower(id);

CREATE INDEX ind_channel_id
ON ResourcesDropped(channel_id);

DELIMITER |
CREATE PROCEDURE add_new_player(IN id BIGINT)
BEGIN
	START TRANSACTION;

	INSERT INTO Tools
	VALUES(NULL, 0, 0, 0, 0, 0);

	SELECT LAST_INSERT_ID() INTO @toolid;

	INSERT INTO Resources
	VALUES(NULL, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
	SELECT LAST_INSERT_ID() INTO @resourceid;

    INSERT INTO Village
    VALUES(NULL, 0, NULL, NULL, 0, 0, 0);
    SELECT LAST_INSERT_ID() INTO @villageid;

    INSERT INTO Tower
    VALUES(NULL, 1, 1, 1);
    SELECT LAST_INSERT_ID() INTO @towerid;

	INSERT INTO Player
	VALUES(id, @toolid, 20, 1, 100, 0, @resourceid, NOW(), 0, 0, UNHEX('898989'), NULL, NULL, 0, 0, NULL, @villageid, @towerid, 0);
	COMMIT;

END|
DELIMITER ;

DELIMITER |
CREATE PROCEDURE drop_player(IN id BIGINT)
BEGIN
    START TRANSACTION;
    SELECT Player.resource_id, Player.tools_id, Player.village_id, Player.tower_id
    INTO @resource_id, @tools_id, @village_id, @tower_id
    FROM Player
    WHERE Player.id = id;

    DELETE FROM Player
    WHERE Player.id = id;

    DELETE FROM Tools
    WHERE Tools.id = @tools_id;

    DELETE FROM Village
    WHERE Village.id = @village_id;

    DELETE FROM TOWER
    WHERE Tower.id = @tower_id;

    DELETE FROM Resources
    WHERE Resources.id = @resource_id;
    COMMIT;
END|
DELIMITER ;



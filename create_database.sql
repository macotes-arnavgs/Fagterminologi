-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema fagterminologi
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema fagterminologi
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `fagterminologi` DEFAULT CHARACTER SET utf8 ;
USE `fagterminologi` ;

-- -----------------------------------------------------
-- Table `fagterminologi`.`bruker`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fagterminologi`.`bruker` (
  `idbruker` INT NOT NULL AUTO_INCREMENT,
  `navn` VARCHAR(45) NOT NULL,
  `passord` VARCHAR(345) NULL,
  PRIMARY KEY (`idbruker`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fagterminologi`.`fag`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fagterminologi`.`fag` (
  `idfag` INT NOT NULL AUTO_INCREMENT,
  `fagnavn` VARCHAR(45) NULL,
  `antall_timer` SMALLINT NULL,
  PRIMARY KEY (`idfag`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fagterminologi`.`begrep`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fagterminologi`.`begrep` (
  `idbegrep` INT NOT NULL AUTO_INCREMENT,
  `begrep` VARCHAR(45) NULL,
  `begrep_definisjon` VARCHAR(400) NULL,
  `fag_idfag` INT NOT NULL,
  PRIMARY KEY (`idbegrep`),
  INDEX `fk_begrep_fag1_idx` (`fag_idfag` ASC) VISIBLE,
  CONSTRAINT `fk_begrep_fag1`
    FOREIGN KEY (`fag_idfag`)
    REFERENCES `fagterminologi`.`fag` (`idfag`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fagterminologi`.`bruker_kan_begrep`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fagterminologi`.`bruker_kan_begrep` (
  `bruker_idbruker` INT NOT NULL,
  `begrep_idbegrep` INT NOT NULL,
  `valg` ENUM("ikke", "litt", "bra") NULL,
  `bruker_definisjon` VARCHAR(400) NULL,
  PRIMARY KEY (`bruker_idbruker`, `begrep_idbegrep`),
  INDEX `fk_bruker_has_begrep_begrep1_idx` (`begrep_idbegrep` ASC) VISIBLE,
  INDEX `fk_bruker_has_begrep_bruker_idx` (`bruker_idbruker` ASC) VISIBLE,
  CONSTRAINT `fk_bruker_has_begrep_bruker`
    FOREIGN KEY (`bruker_idbruker`)
    REFERENCES `fagterminologi`.`bruker` (`idbruker`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_bruker_has_begrep_begrep1`
    FOREIGN KEY (`begrep_idbegrep`)
    REFERENCES `fagterminologi`.`begrep` (`idbegrep`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

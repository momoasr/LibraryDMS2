CREATE DEFINER=`root`@`localhost` PROCEDURE `getBooksByAllGenres`(IN searchArg varchar(255))
BEGIN
    DECLARE genreLength INT DEFAULT 0;
    DECLARE counter INT DEFAULT 0;
    DECLARE genreArg varchar(255) DEFAULT '';

	DROP TABLE IF EXISTS tempGenre;
    CREATE TEMPORARY TABLE tempGenre (
		book_id MEDIUMINT NOT NULL AUTO_INCREMENT,
		genre varchar(255),
        PRIMARY KEY (book_id)
    );

    DROP TABLE IF EXISTS tempBook;    
	CREATE TEMPORARY TABLE tempBook (
		book_id varchar(255) NOT NULL, 
        title varchar(255), 
        author varchar(255),
        genre varchar(255), 
        PRIMARY KEY (book_id)
    );

    INSERT INTO tempGenre (genre)
    SELECT DISTINCT genre 
    FROM book
    ORDER BY genre;

    SELECT COUNT(*) FROM tempGenre INTO genreLength;
    SET counter = 1;

    WHILE counter <= genreLength DO
		SELECT genre FROM tempGenre WHERE book_id = counter INTO genreArg;

        INSERT INTO tempBook    
		SELECT *
		FROM book
		WHERE genre = genreArg
		LIMIT 0, 4;   

		SET counter = counter + 1;
    END WHILE;

    IF searchArg = '' THEN
		SELECT * FROM tempBook
		ORDER BY genre;
	ELSE 
		SELECT * FROM tempBook
        WHERE book_id LIKE CONCAT('%', searchArg, '%')
        OR title LIKE CONCAT('%', searchArg, '%')
        OR author LIKE CONCAT('%', searchArg, '%')
		ORDER BY genre;
    END IF;
END
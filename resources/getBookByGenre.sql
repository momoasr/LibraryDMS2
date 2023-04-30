CREATE DEFINER=`root`@`localhost` PROCEDURE `getBookByGenre`(
	IN genreArg varchar(255), 
    IN startOn INT, 
    IN searchArg varchar(255)
)
BEGIN	
    DECLARE pageSize INT DEFAULT 4;
    SET startOn = startOn * pageSize;
    SET searchArg = IFNULL(searchArg, '');

    IF searchArg = '' THEN
		SELECT *
		FROM book
		WHERE genre = genreArg
		LIMIT startOn, pageSize;
	ELSE 
		SELECT *
		FROM book
		WHERE genre = genreArg
        AND (book_id LIKE CONCAT('%', searchArg, '%')
			OR title LIKE CONCAT('%', searchArg, '%')
			OR author LIKE CONCAT('%', searchArg, '%'))
		LIMIT startOn, pageSize;
    END IF;
END
select n3.n_name from (
	select n_name,n_regionkey from nation where n_regionkey in(0,1)) n1,
	(select n_name,n_regionkey from nation where n_regionkey =1) n2,
	nation n3
	where n3.n_name =n1.n_name and n1.n_regionkey=n2.n_regionkey or n3.n_name!='BRAZIL';
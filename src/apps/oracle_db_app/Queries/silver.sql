        SELECT a.LOGIN_ID, a.LOGIN, a.STATUS, me.LAST_NAME, me.FIRST_NAME, me.SECOND_NAME, me.SNILS, me.EMAIL, l.name as LPU_NAME
FROM emias_cluster.MEDICAL_EMPLOYEE me
         JOIN emias_cluster.MEDICAL_EMPLOYEE_JOB_INFO meji ON me.id = meji.MEDICAL_EMPLOYEE_ID
         JOIN emias_cluster.LPU_DEPARTMENT ld ON meji.DEPARTMENT_LPU_ID = ld.ID
         JOIN emias_cluster.lpu l ON ld.LPU_ID = l.id
         JOIN emias_cluster.ACCOUNT a ON me.ID = a.MEDICAL_EMPLOYEE_ID
         JOIN emias_cluster.REL_ACCOUNT_AND_USER_ROLE raaur ON raaur.LOGIN_ID = a.LOGIN_ID
         LEFT JOIN emias_cluster.ACCOUNT_LPU_BLOCKING_STATUS abs ON raaur.LPU_ID = abs.LPU_ID AND a.LOGIN_ID = abs.account_id
WHERE {condition} AND (meji.JOB_START_DATE < sysdate) AND (meji.JOB_END_DATE > sysdate OR meji.JOB_END_DATE IS NULL) AND a.STATUS='ACTIVE' AND (abs.STATUS = 'ACTIVE' OR abs.STATUS IS NULL)
UNION
SELECT a.LOGIN_ID, a.LOGIN, a.STATUS, me.LAST_NAME, me.FIRST_NAME, me.SECOND_NAME, me.SNILS, me.EMAIL, l.name as LPU_NAME
FROM emias_cluster.MEDICAL_EMPLOYEE me
         JOIN emias_cluster.MEDICAL_EMPLOYEE_JOB_INFO meji ON me.id = meji.MEDICAL_EMPLOYEE_ID
         JOIN emias_cluster.LPU_DEPARTMENT ld ON meji.DEPARTMENT_LPU_ID = ld.ID
         JOIN emias_cluster.lpu l ON ld.LPU_ID = l.id
         JOIN emias_cluster.ACCOUNT a ON me.ID = a.MEDICAL_EMPLOYEE_ID
         JOIN ETD2.REL_ACCOUNT_AND_USER_ROLE raaur ON raaur.LOGIN_ID = a.LOGIN_ID
         LEFT JOIN emias_cluster.ACCOUNT_LPU_BLOCKING_STATUS abs ON raaur.LPU_ID = abs.LPU_ID AND a.LOGIN_ID = abs.account_id
WHERE {condition} AND (meji.JOB_START_DATE < sysdate) AND (meji.JOB_END_DATE > sysdate OR meji.JOB_END_DATE IS NULL) AND a.STATUS='ACTIVE' AND (abs.STATUS = 'ACTIVE' OR abs.STATUS IS NULL)
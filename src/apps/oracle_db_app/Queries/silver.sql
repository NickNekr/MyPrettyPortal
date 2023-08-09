SELECT a.LOGIN_ID, a.LOGIN, a.STATUS, me.LAST_NAME, me.FIRST_NAME, me.SECOND_NAME, me.SNILS, me.PHONE, me.EMAIL, omk.NAME as REGION_NAME, ds.NAME as SPEC_NAME, ds.CODE as SPEC_CODE, ur.USER_ROLE, ur.ID AS USER_ROLE_ID, l.id as LPU_ID, l.name as LPU_NAME, l.OGRN, l2.ID as MO_ID, l2.NAME as MO_NAME
FROM emias_cluster.MEDICAL_EMPLOYEE me
         JOIN emias_cluster.MEDICAL_EMPLOYEE_JOB_INFO meji ON me.id = meji.MEDICAL_EMPLOYEE_ID
         JOIN emias_cluster.LPU_DEPARTMENT ld ON meji.DEPARTMENT_LPU_ID = ld.ID
         JOIN emias_cluster.lpu l ON ld.LPU_ID = l.id
         LEFT JOIN emias_cluster.lpu_group lg ON l.lpu_group_id=lg.id
         LEFT JOIN emias_cluster.lpu l2 ON l2.id=lg.main_lpu_id
         LEFT JOIN emias_cluster.OMK_TE omk ON omk.code = l2.OMK_TE_CODE
         JOIN emias_cluster.DOC_SPECIALITY ds on meji.SPECIALITY_ID=ds.CODE
         JOIN emias_cluster.ACCOUNT a ON me.ID = a.MEDICAL_EMPLOYEE_ID
         JOIN emias_cluster.REL_ACCOUNT_AND_USER_ROLE raaur ON raaur.LOGIN_ID = a.LOGIN_ID
         JOIN emias_cluster.USER_ROLE ur ON raaur.USER_ROLE_ID = ur.ID
         JOIN emias_cluster.lpu l3 ON raaur.LPU_ID = l3.id
         JOIN emias_cluster.lpu_group lg2 ON l3.lpu_group_id=lg2.id AND lg2.main_lpu_id = lg.main_lpu_id
         LEFT JOIN emias_cluster.ACCOUNT_LPU_BLOCKING_STATUS abs ON raaur.LPU_ID = abs.LPU_ID AND a.LOGIN_ID = abs.account_id
WHERE a.LOGIN = {login} AND (meji.JOB_START_DATE < sysdate) AND (meji.JOB_END_DATE > sysdate OR meji.JOB_END_DATE IS NULL) AND a.STATUS='ACTIVE' AND (abs.STATUS = 'ACTIVE' OR abs.STATUS IS NULL)
UNION
SELECT a.LOGIN_ID, a.LOGIN, a.STATUS, me.LAST_NAME, me.FIRST_NAME, me.SECOND_NAME, me.SNILS, me.PHONE, me.EMAIL, omk.NAME as REGION_NAME, ds.NAME as SPEC_NAME, ds.CODE as SPEC_CODE, ur.USER_ROLE, ur.ID AS USER_ROLE_ID, l.id as LPU_ID, l.name as LPU_NAME, l.OGRN, l2.ID as MO_ID, l2.NAME as MO_NAME
FROM emias_cluster.MEDICAL_EMPLOYEE me
         JOIN emias_cluster.MEDICAL_EMPLOYEE_JOB_INFO meji ON me.id = meji.MEDICAL_EMPLOYEE_ID
         JOIN emias_cluster.LPU_DEPARTMENT ld ON meji.DEPARTMENT_LPU_ID = ld.ID
         JOIN emias_cluster.lpu l ON ld.LPU_ID = l.id
         LEFT JOIN emias_cluster.lpu_group lg ON l.lpu_group_id=lg.id
         LEFT JOIN emias_cluster.lpu l2 ON l2.id=lg.main_lpu_id
         LEFT JOIN emias_cluster.OMK_TE omk ON omk.code = l2.OMK_TE_CODE
         JOIN emias_cluster.DOC_SPECIALITY ds on meji.SPECIALITY_ID=ds.CODE
         JOIN emias_cluster.ACCOUNT a ON me.ID = a.MEDICAL_EMPLOYEE_ID
         JOIN ETD2.REL_ACCOUNT_AND_USER_ROLE raaur ON raaur.LOGIN_ID = a.LOGIN_ID
         JOIN ETD2.USER_ROLE ur ON raaur.USER_ROLE_ID = ur.ID
         JOIN emias_cluster.lpu l3 ON raaur.LPU_ID = l3.id
         JOIN emias_cluster.lpu_group lg2 ON l3.lpu_group_id=lg2.id AND lg2.main_lpu_id = lg.main_lpu_id
         LEFT JOIN emias_cluster.ACCOUNT_LPU_BLOCKING_STATUS abs ON raaur.LPU_ID = abs.LPU_ID AND a.LOGIN_ID = abs.account_id
WHERE a.LOGIN = {login} AND (meji.JOB_START_DATE < sysdate) AND (meji.JOB_END_DATE > sysdate OR meji.JOB_END_DATE IS NULL) AND a.STATUS='ACTIVE' AND (abs.STATUS = 'ACTIVE' OR abs.STATUS IS NULL)
UNION
SELECT a.LOGIN_ID, a.LOGIN, a.STATUS, me.LAST_NAME, me.FIRST_NAME, me.SECOND_NAME, me.SNILS, me.PHONE, me.EMAIL,omk.NAME as REGION_NAME, ds.NAME as SPEC_NAME, ds.CODE as SPEC_CODE, ur.USER_ROLE, ur.ID AS USER_ROLE_ID, l.id as LPU_ID, l.name as LPU_NAME, l.OGRN, l2.ID as MO_ID, l2.NAME as MO_NAME
FROM emias_cluster.MEDICAL_EMPLOYEE me
         JOIN emias_cluster.MEDICAL_EMPLOYEE_JOB_INFO meji ON me.id = meji.MEDICAL_EMPLOYEE_ID
         JOIN emias_cluster.LPU_DEPARTMENT ld ON meji.DEPARTMENT_LPU_ID = ld.ID
         JOIN emias_cluster.lpu l ON ld.LPU_ID = l.id
         LEFT JOIN emias_cluster.lpu_group lg ON l.lpu_group_id=lg.id
         LEFT JOIN emias_cluster.lpu l2 ON l2.id=lg.main_lpu_id
         LEFT JOIN emias_cluster.OMK_TE omk ON omk.code = l2.OMK_TE_CODE
         JOIN emias_cluster.DOC_SPECIALITY ds on meji.SPECIALITY_ID=ds.CODE
         JOIN emias_cluster.ACCOUNT a ON me.ID = a.MEDICAL_EMPLOYEE_ID
         JOIN emias_cluster.REL_ACCOUNT_AND_USER_ROLE raaur ON raaur.LOGIN_ID = a.LOGIN_ID
         JOIN emias_cluster.USER_ROLE ur ON raaur.USER_ROLE_ID = ur.ID AND raaur.LPU_ID = l.id
         LEFT JOIN emias_cluster.ACCOUNT_LPU_BLOCKING_STATUS abs ON raaur.LPU_ID = abs.LPU_ID AND a.LOGIN_ID = abs.account_id
WHERE a.LOGIN = {login} AND (meji.JOB_START_DATE < sysdate) AND (meji.JOB_END_DATE > sysdate OR meji.JOB_END_DATE IS NULL) AND a.STATUS='ACTIVE' AND (abs.STATUS = 'ACTIVE' OR abs.STATUS IS NULL)
UNION
SELECT a.LOGIN_ID, a.LOGIN, a.STATUS, me.LAST_NAME, me.FIRST_NAME, me.SECOND_NAME, me.SNILS, me.PHONE, me.EMAIL, omk.NAME as REGION_NAME, ds.NAME as SPEC_NAME, ds.CODE as SPEC_CODE, ur.USER_ROLE, ur.ID AS USER_ROLE_ID, l.id as LPU_ID, l.name as LPU_NAME, l.OGRN, l2.ID as MO_ID, l2.NAME as MO_NAME
FROM emias_cluster.MEDICAL_EMPLOYEE me
         JOIN emias_cluster.MEDICAL_EMPLOYEE_JOB_INFO meji ON me.id = meji.MEDICAL_EMPLOYEE_ID
         JOIN emias_cluster.LPU_DEPARTMENT ld ON meji.DEPARTMENT_LPU_ID = ld.ID
         JOIN emias_cluster.lpu l ON ld.LPU_ID = l.id
         LEFT JOIN emias_cluster.lpu_group lg ON l.lpu_group_id=lg.id
         LEFT JOIN emias_cluster.lpu l2 ON l2.id=lg.main_lpu_id
         LEFT JOIN emias_cluster.OMK_TE omk ON omk.code = l2.OMK_TE_CODE
         JOIN emias_cluster.DOC_SPECIALITY ds on meji.SPECIALITY_ID=ds.CODE
         JOIN emias_cluster.ACCOUNT a ON me.ID = a.MEDICAL_EMPLOYEE_ID
         JOIN ETD2.REL_ACCOUNT_AND_USER_ROLE raaur ON raaur.LOGIN_ID = a.LOGIN_ID
         JOIN ETD2.USER_ROLE ur ON raaur.USER_ROLE_ID = ur.ID AND raaur.LPU_ID = l.id
         LEFT JOIN emias_cluster.ACCOUNT_LPU_BLOCKING_STATUS abs ON raaur.LPU_ID = abs.LPU_ID AND a.LOGIN_ID = abs.account_id
WHERE a.LOGIN = {login} AND (meji.JOB_START_DATE < sysdate) AND (meji.JOB_END_DATE > sysdate OR meji.JOB_END_DATE IS NULL) AND a.STATUS='ACTIVE' AND (abs.STATUS = 'ACTIVE' OR abs.STATUS IS NULL)
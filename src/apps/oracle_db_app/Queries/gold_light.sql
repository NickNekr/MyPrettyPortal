SELECT a.LOGIN, me.LAST_NAME, me.FIRST_NAME, me.SECOND_NAME, me.SNILS, me.PHONE, omk.NAME as REGION_NAME, me.EMAIL, ds.NAME as SPEC_NAME, ds.CODE as SPEC_CODE,
       l.id as LPU_ID, l.name as LPU_NAME, l.OGRN, l2.ID as MO_ID, l2.NAME as MO_NAME, meji.JOB_START_DATE, meji.JOB_END_DATE
FROM emias_cluster.MEDICAL_EMPLOYEE me
JOIN emias_cluster.MEDICAL_EMPLOYEE_JOB_INFO meji ON me.id = meji.MEDICAL_EMPLOYEE_ID
JOIN emias_cluster.LPU_DEPARTMENT ld ON meji.DEPARTMENT_LPU_ID = ld.ID
JOIN emias_cluster.lpu l ON ld.LPU_ID = l.id
LEFT JOIN emias_cluster.lpu_group lg ON l.lpu_group_id=lg.id
LEFT JOIN emias_cluster.lpu l2 ON l2.id=lg.main_lpu_id
LEFT JOIN emias_cluster.OMK_TE omk ON omk.code = l2.OMK_TE_CODE
JOIN emias_cluster.DOC_SPECIALITY ds on meji.SPECIALITY_ID=ds.CODE
JOIN emias_cluster.ACCOUNT a ON me.ID = a.MEDICAL_EMPLOYEE_ID
WHERE (meji.JOB_START_DATE < sysdate) AND (meji.JOB_END_DATE > sysdate OR meji.JOB_END_DATE IS NULL) AND a.STATUS='ACTIVE'
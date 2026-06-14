-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Create municipalities table
CREATE TABLE IF NOT EXISTS municipios (
    id          SERIAL PRIMARY KEY,
    codigo_ibge VARCHAR(7)     NOT NULL UNIQUE,
    nome        VARCHAR(100)   NOT NULL,
    uf          VARCHAR(2)     NOT NULL,
    latitude    NUMERIC(10, 7) NOT NULL,
    longitude   NUMERIC(10, 7) NOT NULL,
    geom        GEOMETRY(Point, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_municipios_geom ON municipios USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_municipios_nome ON municipios (lower(nome));
CREATE INDEX IF NOT EXISTS idx_municipios_uf   ON municipios (uf);

-- Seed: representative sample of Brazilian municipalities (5570 total)
-- Full dataset loaded via CSV import in entrypoint; this seed covers major cities
-- so the application works out-of-the-box without additional data loading.

INSERT INTO municipios (codigo_ibge, nome, uf, latitude, longitude, geom) VALUES
-- São Paulo
('3550308','São Paulo','SP',-23.5505,-46.6333,ST_SetSRID(ST_MakePoint(-46.6333,-23.5505),4326)),
('3509502','Campinas','SP',-22.9064,-47.0616,ST_SetSRID(ST_MakePoint(-47.0616,-22.9064),4326)),
('3552205','Sorocaba','SP',-23.5015,-47.4526,ST_SetSRID(ST_MakePoint(-47.4526,-23.5015),4326)),
('3525904','Jundiaí','SP',-23.1864,-46.8841,ST_SetSRID(ST_MakePoint(-46.8841,-23.1864),4326)),
('3518800','Guarulhos','SP',-23.4543,-46.5338,ST_SetSRID(ST_MakePoint(-46.5338,-23.4543),4326)),
('3548708','Santo André','SP',-23.6639,-46.5383,ST_SetSRID(ST_MakePoint(-46.5383,-23.6639),4326)),
('3548807','Santos','SP',-23.9619,-46.3042,ST_SetSRID(ST_MakePoint(-46.3042,-23.9619),4326)),
('3549805','São Bernardo do Campo','SP',-23.6939,-46.5650,ST_SetSRID(ST_MakePoint(-46.5650,-23.6939),4326)),
('3549904','São Caetano do Sul','SP',-23.6228,-46.5500,ST_SetSRID(ST_MakePoint(-46.5500,-23.6228),4326)),
('3513801','Diadema','SP',-23.6860,-46.6236,ST_SetSRID(ST_MakePoint(-46.6236,-23.6860),4326)),
('3529401','Mauá','SP',-23.6678,-46.4606,ST_SetSRID(ST_MakePoint(-46.4606,-23.6678),4326)),
('3544103','Ribeirão Preto','SP',-21.1775,-47.8103,ST_SetSRID(ST_MakePoint(-47.8103,-21.1775),4326)),
('3554102','São José dos Campos','SP',-23.1794,-45.8869,ST_SetSRID(ST_MakePoint(-45.8869,-23.1794),4326)),
('3556206','São José do Rio Preto','SP',-20.8197,-49.3794,ST_SetSRID(ST_MakePoint(-49.3794,-20.8197),4326)),
('3530607','Osasco','SP',-23.5325,-46.7919,ST_SetSRID(ST_MakePoint(-46.7919,-23.5325),4326)),
('3501608','Americana','SP',-22.7389,-47.3314,ST_SetSRID(ST_MakePoint(-47.3314,-22.7389),4326)),
('3543402','Piracicaba','SP',-22.7253,-47.6492,ST_SetSRID(ST_MakePoint(-47.6492,-22.7253),4326)),
('3545803','Santa Bárbara d''Oeste','SP',-22.7539,-47.4136,ST_SetSRID(ST_MakePoint(-47.4136,-22.7539),4326)),
('3506003','Barueri','SP',-23.5114,-46.8756,ST_SetSRID(ST_MakePoint(-46.8756,-23.5114),4326)),
('3522604','Indaiatuba','SP',-23.0900,-47.2181,ST_SetSRID(ST_MakePoint(-47.2181,-23.0900),4326)),
('3557303','Sumaré','SP',-22.8217,-47.2672,ST_SetSRID(ST_MakePoint(-47.2672,-22.8217),4326)),
('3513108','Cubatão','SP',-23.8978,-46.4256,ST_SetSRID(ST_MakePoint(-46.4256,-23.8978),4326)),
('3537107','Praia Grande','SP',-24.0056,-46.4033,ST_SetSRID(ST_MakePoint(-46.4033,-24.0056),4326)),
('3557208','Suzano','SP',-23.5428,-46.3106,ST_SetSRID(ST_MakePoint(-46.3106,-23.5428),4326)),
('3502804','Araçatuba','SP',-21.2092,-50.4419,ST_SetSRID(ST_MakePoint(-50.4419,-21.2092),4326)),
('3505708','Bauru','SP',-22.3147,-49.0608,ST_SetSRID(ST_MakePoint(-49.0608,-22.3147),4326)),
('3538709','Presidente Prudente','SP',-22.1256,-51.3886,ST_SetSRID(ST_MakePoint(-51.3886,-22.1256),4326)),
('3541000','Registro','SP',-24.4878,-47.8439,ST_SetSRID(ST_MakePoint(-47.8439,-24.4878),4326)),
('3534401','Paulínia','SP',-22.7614,-47.1556,ST_SetSRID(ST_MakePoint(-47.1556,-22.7614),4326)),
('3504503','Araraquara','SP',-21.7942,-48.1758,ST_SetSRID(ST_MakePoint(-48.1758,-21.7942),4326)),
('3504206','Araras','SP',-22.3581,-47.3833,ST_SetSRID(ST_MakePoint(-47.3833,-22.3581),4326)),
('3510609','Cajamar','SP',-23.3564,-46.8761,ST_SetSRID(ST_MakePoint(-46.8761,-23.3564),4326)),
('3513504','Cotia','SP',-23.6036,-46.9192,ST_SetSRID(ST_MakePoint(-46.9192,-23.6036),4326)),
('3516200','Embu das Artes','SP',-23.6511,-46.8519,ST_SetSRID(ST_MakePoint(-46.8519,-23.6511),4326)),
('3523107','Itapevi','SP',-23.5486,-47.0697,ST_SetSRID(ST_MakePoint(-47.0697,-23.5486),4326)),
('3525003','Jaboticabal','SP',-21.2556,-48.3200,ST_SetSRID(ST_MakePoint(-48.3200,-21.2556),4326)),
('3526902','Leme','SP',-22.1853,-47.3883,ST_SetSRID(ST_MakePoint(-47.3883,-22.1853),4326)),
('3529005','Marília','SP',-22.2133,-49.9458,ST_SetSRID(ST_MakePoint(-49.9458,-22.2133),4326)),
('3531803','Nova Odessa','SP',-22.7814,-47.2997,ST_SetSRID(ST_MakePoint(-47.2997,-22.7814),4326)),
('3541406','Rio Claro','SP',-22.4156,-47.5642,ST_SetSRID(ST_MakePoint(-47.5642,-22.4156),4326)),
('3557401','Taboão da Serra','SP',-23.6061,-46.7608,ST_SetSRID(ST_MakePoint(-46.7608,-23.6061),4326)),
('3558006','Taubaté','SP',-23.0256,-45.5553,ST_SetSRID(ST_MakePoint(-45.5553,-23.0256),4326)),
('3561101','Valinhos','SP',-22.9711,-47.0008,ST_SetSRID(ST_MakePoint(-47.0008,-22.9711),4326)),
('3556453','São Paulo Guarujá','SP',-23.9931,-46.2564,ST_SetSRID(ST_MakePoint(-46.2564,-23.9931),4326)),
('3519071','Hortolândia','SP',-22.8575,-47.2197,ST_SetSRID(ST_MakePoint(-47.2197,-22.8575),4326)),
('3522000','Itatiba','SP',-23.0058,-46.8381,ST_SetSRID(ST_MakePoint(-46.8381,-23.0058),4326)),
('3561901','Vinhedo','SP',-23.0297,-46.9750,ST_SetSRID(ST_MakePoint(-46.9750,-23.0297),4326)),
('3563238','Votorantim','SP',-23.5483,-47.4372,ST_SetSRID(ST_MakePoint(-47.4372,-23.5483),4326)),
('3508801','Botucatu','SP',-22.8861,-48.4453,ST_SetSRID(ST_MakePoint(-48.4453,-22.8861),4326)),
('3525300','Jacareí','SP',-23.3053,-45.9653,ST_SetSRID(ST_MakePoint(-45.9653,-23.3053),4326)),
-- Rio de Janeiro
('3304557','Rio de Janeiro','RJ',-22.9068,-43.1729,ST_SetSRID(ST_MakePoint(-43.1729,-22.9068),4326)),
('3303500','Niterói','RJ',-22.8836,-43.1036,ST_SetSRID(ST_MakePoint(-43.1036,-22.8836),4326)),
('3301702','Duque de Caxias','RJ',-22.7856,-43.3117,ST_SetSRID(ST_MakePoint(-43.3117,-22.7856),4326)),
('3304904','São Gonçalo','RJ',-22.8269,-43.0539,ST_SetSRID(ST_MakePoint(-43.0539,-22.8269),4326)),
('3301009','Belford Roxo','RJ',-22.7644,-43.4003,ST_SetSRID(ST_MakePoint(-43.4003,-22.7644),4326)),
('3302858','Mesquita','RJ',-22.8178,-43.4331,ST_SetSRID(ST_MakePoint(-43.4331,-22.8178),4326)),
('3302205','Itaboraí','RJ',-22.7658,-42.8597,ST_SetSRID(ST_MakePoint(-42.8597,-22.7658),4326)),
('3303302','Nova Iguaçu','RJ',-22.7592,-43.4511,ST_SetSRID(ST_MakePoint(-43.4511,-22.7592),4326)),
('3305109','São João de Meriti','RJ',-22.8036,-43.3722,ST_SetSRID(ST_MakePoint(-43.3722,-22.8036),4326)),
('3303906','Petrópolis','RJ',-22.5050,-43.1786,ST_SetSRID(ST_MakePoint(-43.1786,-22.5050),4326)),
('3306305','Volta Redonda','RJ',-22.5231,-44.1042,ST_SetSRID(ST_MakePoint(-44.1042,-22.5231),4326)),
('3302403','Itaguaí','RJ',-22.8631,-43.7758,ST_SetSRID(ST_MakePoint(-43.7758,-22.8631),4326)),
('3305802','Teresópolis','RJ',-22.4119,-42.9658,ST_SetSRID(ST_MakePoint(-42.9658,-22.4119),4326)),
('3300456','Angra dos Reis','RJ',-23.0067,-44.3183,ST_SetSRID(ST_MakePoint(-44.3183,-23.0067),4326)),
('3303203','Nilópolis','RJ',-22.8061,-43.4239,ST_SetSRID(ST_MakePoint(-43.4239,-22.8061),4326)),
('3301603','Campos dos Goytacazes','RJ',-21.7542,-41.3244,ST_SetSRID(ST_MakePoint(-41.3244,-21.7542),4326)),
('3302007','Macaé','RJ',-22.3711,-41.7869,ST_SetSRID(ST_MakePoint(-41.7869,-22.3711),4326)),
-- Minas Gerais
('3106200','Belo Horizonte','MG',-19.9167,-43.9345,ST_SetSRID(ST_MakePoint(-43.9345,-19.9167),4326)),
('3170206','Uberlândia','MG',-18.9186,-48.2772,ST_SetSRID(ST_MakePoint(-48.2772,-18.9186),4326)),
('3143302','Montes Claros','MG',-16.7286,-43.8611,ST_SetSRID(ST_MakePoint(-43.8611,-16.7286),4326)),
('3118601','Contagem','MG',-19.9317,-44.0536,ST_SetSRID(ST_MakePoint(-44.0536,-19.9317),4326)),
('3122306','Juiz de Fora','MG',-21.7642,-43.3503,ST_SetSRID(ST_MakePoint(-43.3503,-21.7642),4326)),
('3152501','Ribeirão das Neves','MG',-19.7681,-44.0844,ST_SetSRID(ST_MakePoint(-44.0844,-19.7681),4326)),
('3171303','Uberaba','MG',-19.7481,-47.9317,ST_SetSRID(ST_MakePoint(-47.9317,-19.7481),4326)),
('3167202','Sete Lagoas','MG',-19.4653,-44.2472,ST_SetSRID(ST_MakePoint(-44.2472,-19.4653),4326)),
('3107901','Betim','MG',-19.9675,-44.1983,ST_SetSRID(ST_MakePoint(-44.1983,-19.9675),4326)),
('3131307','Governador Valadares','MG',-18.8511,-41.9494,ST_SetSRID(ST_MakePoint(-41.9494,-18.8511),4326)),
('3162922','Santa Luzia','MG',-19.7700,-43.8519,ST_SetSRID(ST_MakePoint(-43.8519,-19.7700),4326)),
('3157807','Sabará','MG',-19.8869,-43.8072,ST_SetSRID(ST_MakePoint(-43.8072,-19.8869),4326)),
('3130706','Ipatinga','MG',-19.4719,-42.5364,ST_SetSRID(ST_MakePoint(-42.5364,-19.4719),4326)),
('3145901','Patos de Minas','MG',-18.5786,-46.5183,ST_SetSRID(ST_MakePoint(-46.5183,-18.5786),4326)),
-- Paraná
('4106902','Curitiba','PR',-25.4278,-49.2731,ST_SetSRID(ST_MakePoint(-49.2731,-25.4278),4326)),
('4109401','Londrina','PR',-23.3044,-51.1694,ST_SetSRID(ST_MakePoint(-51.1694,-23.3044),4326)),
('4115200','Maringá','PR',-23.4206,-51.9331,ST_SetSRID(ST_MakePoint(-51.9331,-23.4206),4326)),
('4104808','Campo Grande (PR)','PR',-25.4950,-49.3050,ST_SetSRID(ST_MakePoint(-49.3050,-25.4950),4326)),
('4113700','Ponta Grossa','PR',-25.0944,-50.1619,ST_SetSRID(ST_MakePoint(-50.1619,-25.0944),4326)),
('4127700','São José dos Pinhais','PR',-25.5372,-49.2081,ST_SetSRID(ST_MakePoint(-49.2081,-25.5372),4326)),
('4104055','Cascavel','PR',-24.9578,-53.4597,ST_SetSRID(ST_MakePoint(-53.4597,-24.9578),4326)),
('4106209','Colombo','PR',-25.2928,-49.2239,ST_SetSRID(ST_MakePoint(-49.2239,-25.2928),4326)),
('4118402','Pinhais','PR',-25.4431,-49.1922,ST_SetSRID(ST_MakePoint(-49.1922,-25.4431),4326)),
('4125506','Sarandi','PR',-23.4408,-51.8769,ST_SetSRID(ST_MakePoint(-51.8769,-23.4408),4326)),
('4103305','Apucarana','PR',-23.5508,-51.4608,ST_SetSRID(ST_MakePoint(-51.4608,-23.5508),4326)),
('4102406','Almirante Tamandaré','PR',-25.3219,-49.2981,ST_SetSRID(ST_MakePoint(-49.2981,-25.3219),4326)),
-- Rio Grande do Sul
('4314902','Porto Alegre','RS',-30.0277,-51.2287,ST_SetSRID(ST_MakePoint(-51.2287,-30.0277),4326)),
('4304606','Caxias do Sul','RS',-29.1681,-51.1794,ST_SetSRID(ST_MakePoint(-51.1794,-29.1681),4326)),
('4316907','Santa Maria','RS',-29.6842,-53.8069,ST_SetSRID(ST_MakePoint(-53.8069,-29.6842),4326)),
('4313409','Novo Hamburgo','RS',-29.6783,-51.1303,ST_SetSRID(ST_MakePoint(-51.1303,-29.6783),4326)),
('4306403','Gravataí','RS',-29.9436,-51.0597,ST_SetSRID(ST_MakePoint(-51.0597,-29.9436),4326)),
('4308904','Ijuí','RS',-28.3878,-53.9150,ST_SetSRID(ST_MakePoint(-53.9150,-28.3878),4326)),
('4309209','Passo Fundo','RS',-28.2622,-52.4083,ST_SetSRID(ST_MakePoint(-52.4083,-28.2622),4326)),
('4303103','Canoas','RS',-29.9178,-51.1839,ST_SetSRID(ST_MakePoint(-51.1839,-29.9178),4326)),
('4312401','Pelotas','RS',-31.7719,-52.3425,ST_SetSRID(ST_MakePoint(-52.3425,-31.7719),4326)),
('4318705','São Leopoldo','RS',-29.7600,-51.1489,ST_SetSRID(ST_MakePoint(-51.1489,-29.7600),4326)),
('4307708','Guaíba','RS',-30.1133,-51.3239,ST_SetSRID(ST_MakePoint(-51.3239,-30.1133),4326)),
('4305108','Erechim','RS',-27.6344,-52.2739,ST_SetSRID(ST_MakePoint(-52.2739,-27.6344),4326)),
-- Santa Catarina
('4205407','Florianópolis','SC',-27.5954,-48.5480,ST_SetSRID(ST_MakePoint(-48.5480,-27.5954),4326)),
('4202404','Blumenau','SC',-26.9194,-49.0661,ST_SetSRID(ST_MakePoint(-49.0661,-26.9194),4326)),
('4218707','São José','SC',-27.5942,-48.6272,ST_SetSRID(ST_MakePoint(-48.6272,-27.5942),4326)),
('4204202','Criciúma','SC',-28.6778,-49.3697,ST_SetSRID(ST_MakePoint(-49.3697,-28.6778),4326)),
('4205506','Florianópolis Palhoça','SC',-27.6444,-48.6680,ST_SetSRID(ST_MakePoint(-48.6680,-27.6444),4326)),
('4209102','Joinville','SC',-26.3044,-48.8487,ST_SetSRID(ST_MakePoint(-48.8487,-26.3044),4326)),
('4203808','Chapecó','SC',-27.0992,-52.6186,ST_SetSRID(ST_MakePoint(-52.6186,-27.0992),4326)),
('4209300','Lages','SC',-27.8161,-50.3261,ST_SetSRID(ST_MakePoint(-50.3261,-27.8161),4326)),
('4202008','Balneário Camboriú','SC',-26.9903,-48.6349,ST_SetSRID(ST_MakePoint(-48.6349,-26.9903),4326)),
('4215604','Palhoça','SC',-27.6444,-48.6683,ST_SetSRID(ST_MakePoint(-48.6683,-27.6444),4326)),
-- Bahia
('2927408','Salvador','BA',-12.9714,-38.5014,ST_SetSRID(ST_MakePoint(-38.5014,-12.9714),4326)),
('2910800','Feira de Santana','BA',-12.2664,-38.9663,ST_SetSRID(ST_MakePoint(-38.9663,-12.2664),4326)),
('2919553','Lauro de Freitas','BA',-12.8972,-38.3297,ST_SetSRID(ST_MakePoint(-38.3297,-12.8972),4326)),
('2910727','Camaçari','BA',-12.6981,-38.3244,ST_SetSRID(ST_MakePoint(-38.3244,-12.6981),4326)),
('2924900','Juazeiro','BA',-9.4122,-40.5017,ST_SetSRID(ST_MakePoint(-40.5017,-9.4122),4326)),
('2933307','Vitória da Conquista','BA',-14.8661,-40.8444,ST_SetSRID(ST_MakePoint(-40.8444,-14.8661),4326)),
('2910529','Caetité','BA',-14.0681,-42.4806,ST_SetSRID(ST_MakePoint(-42.4806,-14.0681),4326)),
('2918407','Ilhéus','BA',-14.7894,-39.0486,ST_SetSRID(ST_MakePoint(-39.0486,-14.7894),4326)),
('2930709','Simões Filho','BA',-12.7836,-38.4019,ST_SetSRID(ST_MakePoint(-38.4019,-12.7836),4326)),
-- Pernambuco
('2611606','Recife','PE',-8.0539,-34.8811,ST_SetSRID(ST_MakePoint(-34.8811,-8.0539),4326)),
('2604106','Caruaru','PE',-8.2760,-35.9753,ST_SetSRID(ST_MakePoint(-35.9753,-8.2760),4326)),
('2607901','Jaboatão dos Guararapes','PE',-8.1131,-35.0147,ST_SetSRID(ST_MakePoint(-35.0147,-8.1131),4326)),
('2611101','Olinda','PE',-7.9994,-34.8453,ST_SetSRID(ST_MakePoint(-34.8453,-7.9994),4326)),
('2609600','Paulista','PE',-7.9436,-34.8781,ST_SetSRID(ST_MakePoint(-34.8781,-7.9436),4326)),
('2614105','Petrolina','PE',-9.3961,-40.5008,ST_SetSRID(ST_MakePoint(-40.5008,-9.3961),4326)),
('2602902','Camarajibe','PE',-8.0217,-34.9803,ST_SetSRID(ST_MakePoint(-34.9803,-8.0217),4326)),
('2610707','Mossoró','RN',-5.1875,-37.3444,ST_SetSRID(ST_MakePoint(-37.3444,-5.1875),4326)),
-- Ceará
('2304400','Fortaleza','CE',-3.7172,-38.5433,ST_SetSRID(ST_MakePoint(-38.5433,-3.7172),4326)),
('2307650','Maracanaú','CE',-3.8711,-38.6272,ST_SetSRID(ST_MakePoint(-38.6272,-3.8711),4326)),
('2303709','Caucaia','CE',-3.7228,-38.6633,ST_SetSRID(ST_MakePoint(-38.6633,-3.7228),4326)),
('2311405','Sobral','CE',-3.6861,-40.3500,ST_SetSRID(ST_MakePoint(-40.3500,-3.6861),4326)),
('2304203','Crato','CE',-7.2317,-39.4094,ST_SetSRID(ST_MakePoint(-39.4094,-7.2317),4326)),
('2305506','Juazeiro do Norte','CE',-7.2131,-39.3153,ST_SetSRID(ST_MakePoint(-39.3153,-7.2131),4326)),
-- Amazonas
('1302603','Manaus','AM',-3.1190,-60.0217,ST_SetSRID(ST_MakePoint(-60.0217,-3.1190),4326)),
('1300607','Itacoatiara','AM',-3.1439,-58.4439,ST_SetSRID(ST_MakePoint(-58.4439,-3.1439),4326)),
('1303569','Parintins','AM',-2.6275,-56.7358,ST_SetSRID(ST_MakePoint(-56.7358,-2.6275),4326)),
-- Pará
('1501402','Belém','PA',-1.4558,-48.5039,ST_SetSRID(ST_MakePoint(-48.5039,-1.4558),4326)),
('1502400','Ananindeua','PA',-1.3658,-48.3728,ST_SetSRID(ST_MakePoint(-48.3728,-1.3658),4326)),
('1508100','Santarém','PA',-2.4426,-54.7081,ST_SetSRID(ST_MakePoint(-54.7081,-2.4426),4326)),
('1505064','Marabá','PA',-5.3686,-49.1181,ST_SetSRID(ST_MakePoint(-49.1181,-5.3686),4326)),
-- Goiás
('5208707','Goiânia','GO',-16.6869,-49.2648,ST_SetSRID(ST_MakePoint(-49.2648,-16.6869),4326)),
('5201405','Aparecida de Goiânia','GO',-16.8231,-49.2439,ST_SetSRID(ST_MakePoint(-49.2439,-16.8231),4326)),
('5221858','Trindade','GO',-16.6503,-49.4878,ST_SetSRID(ST_MakePoint(-49.4878,-16.6503),4326)),
('5209937','Luziânia','GO',-16.2528,-47.9481,ST_SetSRID(ST_MakePoint(-47.9481,-16.2528),4326)),
('5218805','Senador Canedo','GO',-16.7089,-49.0911,ST_SetSRID(ST_MakePoint(-49.0911,-16.7089),4326)),
('5200258','Águas Lindas de Goiás','GO',-15.7461,-48.2822,ST_SetSRID(ST_MakePoint(-48.2822,-15.7461),4326)),
('5219753','Valparaíso de Goiás','GO',-16.0708,-47.9919,ST_SetSRID(ST_MakePoint(-47.9919,-16.0708),4326)),
-- Distrito Federal
('5300108','Brasília','DF',-15.7801,-47.9292,ST_SetSRID(ST_MakePoint(-47.9292,-15.7801),4326)),
-- Mato Grosso do Sul
('5002704','Campo Grande','MS',-20.4428,-54.6461,ST_SetSRID(ST_MakePoint(-54.6461,-20.4428),4326)),
('5003207','Corumbá','MS',-19.0083,-57.6542,ST_SetSRID(ST_MakePoint(-57.6542,-19.0083),4326)),
('5005103','Dourados','MS',-22.2211,-54.8056,ST_SetSRID(ST_MakePoint(-54.8056,-22.2211),4326)),
-- Mato Grosso
('5103403','Cuiabá','MT',-15.5989,-56.0949,ST_SetSRID(ST_MakePoint(-56.0949,-15.5989),4326)),
('5103205','Várzea Grande','MT',-15.6469,-56.1328,ST_SetSRID(ST_MakePoint(-56.1328,-15.6469),4326)),
('5107040','Sinop','MT',-11.8611,-55.5044,ST_SetSRID(ST_MakePoint(-55.5044,-11.8611),4326)),
-- Espírito Santo
('3205309','Vitória','ES',-20.3155,-40.3128,ST_SetSRID(ST_MakePoint(-40.3128,-20.3155),4326)),
('3201308','Cariacica','ES',-20.2639,-40.4194,ST_SetSRID(ST_MakePoint(-40.4194,-20.2639),4326)),
('3205200','Vila Velha','ES',-20.3297,-40.2922,ST_SetSRID(ST_MakePoint(-40.2922,-20.3297),4326)),
('3205010','Serra','ES',-20.1286,-40.3078,ST_SetSRID(ST_MakePoint(-40.3078,-20.1286),4326)),
('3202405','Colatina','ES',-19.5378,-40.6289,ST_SetSRID(ST_MakePoint(-40.6289,-19.5378),4326)),
('3203320','Linhares','ES',-19.3922,-40.0689,ST_SetSRID(ST_MakePoint(-40.0689,-19.3922),4326)),
-- Rio Grande do Norte
('2408102','Natal','RN',-5.7945,-35.2110,ST_SetSRID(ST_MakePoint(-35.2110,-5.7945),4326)),
('2401552','Caicó','RN',-6.4589,-37.0975,ST_SetSRID(ST_MakePoint(-37.0975,-6.4589),4326)),
('2403103','Currais Novos','RN',-6.2597,-36.5219,ST_SetSRID(ST_MakePoint(-36.5219,-6.2597),4326)),
('2408003','Mossoró','RN',-5.1878,-37.3442,ST_SetSRID(ST_MakePoint(-37.3442,-5.1878),4326)),
-- Paraíba
('2507507','João Pessoa','PB',-7.1195,-34.8450,ST_SetSRID(ST_MakePoint(-34.8450,-7.1195),4326)),
('2504009','Campina Grande','PB',-7.2306,-35.8811,ST_SetSRID(ST_MakePoint(-35.8811,-7.2306),4326)),
-- Alagoas
('2704302','Maceió','AL',-9.6658,-35.7350,ST_SetSRID(ST_MakePoint(-35.7350,-9.6658),4326)),
('2702306','Arapiraca','AL',-9.7528,-36.6608,ST_SetSRID(ST_MakePoint(-36.6608,-9.7528),4326)),
-- Sergipe
('2800308','Aracaju','SE',-10.9472,-37.0731,ST_SetSRID(ST_MakePoint(-37.0731,-10.9472),4326)),
('2802106','Lagarto','SE',-10.9167,-37.6500,ST_SetSRID(ST_MakePoint(-37.6500,-10.9167),4326)),
-- Piauí
('2211001','Teresina','PI',-5.0919,-42.8034,ST_SetSRID(ST_MakePoint(-42.8034,-5.0919),4326)),
('2203909','Floriano','PI',-6.7669,-43.0219,ST_SetSRID(ST_MakePoint(-43.0219,-6.7669),4326)),
-- Maranhão
('2111300','São Luís','MA',-2.5391,-44.2829,ST_SetSRID(ST_MakePoint(-44.2829,-2.5391),4326)),
('2105302','Imperatriz','MA',-5.5258,-47.4789,ST_SetSRID(ST_MakePoint(-47.4789,-5.5258),4326)),
('2101400','Bacabal','MA',-4.2256,-44.7858,ST_SetSRID(ST_MakePoint(-44.7858,-4.2256),4326)),
-- Tocantins
('1721000','Palmas','TO',-10.2491,-48.3243,ST_SetSRID(ST_MakePoint(-48.3243,-10.2491),4326)),
('1702109','Araguaína','TO',-7.1928,-48.2039,ST_SetSRID(ST_MakePoint(-48.2039,-7.1928),4326)),
-- Rondônia
('1100205','Porto Velho','RO',-8.7612,-63.9004,ST_SetSRID(ST_MakePoint(-63.9004,-8.7612),4326)),
('1100122','Ji-Paraná','RO',-10.8850,-61.9503,ST_SetSRID(ST_MakePoint(-61.9503,-10.8850),4326)),
-- Acre
('1200401','Rio Branco','AC',-9.9781,-67.8100,ST_SetSRID(ST_MakePoint(-67.8100,-9.9781),4326)),
-- Roraima
('1400100','Boa Vista','RR',2.8197,-60.6733,ST_SetSRID(ST_MakePoint(-60.6733,2.8197),4326)),
-- Amapá
('1600303','Macapá','AP',0.0349,-51.0694,ST_SetSRID(ST_MakePoint(-51.0694,0.0349),4326))
ON CONFLICT (codigo_ibge) DO NOTHING;

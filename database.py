# database.py
import os
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import geopandas as gpd
from geoalchemy2 import Geometry
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        """Inicializa o gerenciador de banco de dados."""
        self.engine = None
        self.SessionLocal = None
        self._create_engine()
    
    def _create_engine(self):
        """Cria a engine de conexão com o banco de dados."""
        try:
            # Obter variáveis de ambiente
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME", "download_car")
            db_user = os.getenv("DB_USER", "postgres")
            db_password = os.getenv("DB_PASSWORD", "postgres")
            db_schema = os.getenv("DB_SCHEMA", "public")
            db_pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
            db_timeout = int(os.getenv("DB_TIMEOUT", "30"))
            
            # Construir URL de conexão
            connection_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            
            # Criar engine com configurações
            self.engine = create_engine(
                connection_url,
                poolclass=QueuePool,
                pool_size=db_pool_size,
                max_overflow=10,
                pool_timeout=db_timeout,
                pool_recycle=3600,
                echo=False  # Set to True for SQL debugging
            )
            
            # Criar session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            logger.info(f"Engine de banco de dados criada com sucesso para {db_host}:{db_port}/{db_name}")
            
        except Exception as e:
            logger.error(f"Erro ao criar engine de banco de dados: {e}")
            raise
    
    def test_connection(self):
        """Testa a conexão com o banco de dados."""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                logger.info("Conexão com banco de dados testada com sucesso")
                return True
        except Exception as e:
            logger.error(f"Erro ao testar conexão com banco de dados: {e}")
            return False
    
    def check_postgis_extension(self):
        """Verifica se a extensão PostGIS está disponível no banco de dados."""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT PostGIS_Version()"))
                postgis_version = result.fetchone()[0]
                logger.info(f"PostGIS versão: {postgis_version}")
                return True
        except Exception as e:
            logger.error(f"PostGIS não está disponível: {e}")
            return False
    
    def sync_shapefile_to_db(self, shapefile_path: str, state: str, polygon_type: str, car_code: Optional[str] = None):
        """
        Sincroniza um shapefile com o banco de dados.
        
        Args:
            shapefile_path: Caminho para o arquivo shapefile
            state: Sigla do estado
            polygon_type: Tipo de polígono
            car_code: Código CAR específico (opcional)
        """
        try:
            # Ler o shapefile com geopandas
            logger.info(f"Lendo shapefile: {shapefile_path}")
            gdf = gpd.read_file(shapefile_path)
            
            if gdf.empty:
                logger.warning("Shapefile está vazio")
                return {"success": False, "message": "Shapefile está vazio"}
            
            # Converter para WGS84 se necessário
            if gdf.crs != 'EPSG:4326':
                logger.info(f"Convertendo CRS de {gdf.crs} para EPSG:4326")
                gdf = gdf.to_crs('EPSG:4326')
            
            # Preparar dados para inserção
            records_to_insert = []
            
            for idx, row in gdf.iterrows():
                # Extrair código CAR da geometria ou propriedades
                car_field = None
                for field in ['CAR', 'cod_imovel', 'COD_IMOVEL', 'car', 'codigo_car']:
                    if field in gdf.columns:
                        car_field = field
                        break
                
                if car_field:
                    current_car_code = str(row[car_field]).strip()
                else:
                    # Se não encontrar campo CAR, usar um código gerado
                    current_car_code = f"{state}_{polygon_type}_{idx}"
                
                # Se um CAR específico foi solicitado, filtrar apenas ele
                if car_code and current_car_code != car_code:
                    continue
                
                # Preparar propriedades como JSON
                properties = {}
                for col in gdf.columns:
                    if col != 'geometry':
                        properties[col] = str(row[col]) if row[col] is not None else None
                
                # Preparar registro
                record = {
                    'car_code': current_car_code,
                    'state': state,
                    'polygon_type': polygon_type,
                    'geometry': row.geometry.wkt if row.geometry else None,
                    'properties': properties
                }
                
                records_to_insert.append(record)
            
            if not records_to_insert:
                logger.warning("Nenhum registro encontrado para inserção")
                return {"success": False, "message": "Nenhum registro encontrado para inserção"}
            
            # Inserir no banco de dados
            with self.SessionLocal() as session:
                for record in records_to_insert:
                    try:
                        # Verificar se já existe
                        existing = session.execute(
                            text("SELECT id FROM car_data WHERE car_code = :car_code"),
                            {"car_code": record['car_code']}
                        ).fetchone()
                        
                        if existing:
                            # Atualizar registro existente
                            update_sql = """
                            UPDATE car_data 
                            SET state = :state, polygon_type = :polygon_type, 
                                geometry = ST_GeomFromText(:geometry, 4326), 
                                properties = :properties, updated_at = CURRENT_TIMESTAMP
                            WHERE car_code = :car_code
                            """
                            session.execute(text(update_sql), record)
                            logger.info(f"Registro atualizado: {record['car_code']}")
                        else:
                            # Inserir novo registro
                            insert_sql = """
                            INSERT INTO car_data (car_code, state, polygon_type, geometry, properties)
                            VALUES (:car_code, :state, :polygon_type, ST_GeomFromText(:geometry, 4326), :properties)
                            """
                            session.execute(text(insert_sql), record)
                            logger.info(f"Registro inserido: {record['car_code']}")
                    
                    except Exception as e:
                        logger.error(f"Erro ao processar registro {record['car_code']}: {e}")
                        continue
                
                session.commit()
            
            logger.info(f"Sincronização concluída. {len(records_to_insert)} registros processados")
            return {
                "success": True,
                "message": f"Sincronização concluída com sucesso",
                "records_processed": len(records_to_insert),
                "state": state,
                "polygon_type": polygon_type
            }
            
        except Exception as e:
            logger.error(f"Erro ao sincronizar shapefile: {e}")
            return {"success": False, "message": f"Erro ao sincronizar shapefile: {str(e)}"}
    
    def get_car_data(self, car_code: Optional[str] = None, state: Optional[str] = None, polygon_type: Optional[str] = None, limit: int = 100):
        """
        Busca dados do CAR no banco de dados.
        
        Args:
            car_code: Código CAR específico
            state: Sigla do estado
            polygon_type: Tipo de polígono
            limit: Limite de resultados
        """
        try:
            query = "SELECT car_code, state, polygon_type, ST_AsText(geometry) as geometry, properties, created_at FROM car_data WHERE 1=1"
            params = {}
            
            if car_code:
                query += " AND car_code = :car_code"
                params['car_code'] = car_code
            
            if state:
                query += " AND state = :state"
                params['state'] = state
            
            if polygon_type:
                query += " AND polygon_type = :polygon_type"
                params['polygon_type'] = polygon_type
            
            query += f" ORDER BY created_at DESC LIMIT {limit}"
            
            with self.SessionLocal() as session:
                result = session.execute(text(query), params)
                records = []
                
                for row in result:
                    records.append({
                        'car_code': row.car_code,
                        'state': row.state,
                        'polygon_type': row.polygon_type,
                        'geometry': row.geometry,
                        'properties': row.properties,
                        'created_at': row.created_at.isoformat() if row.created_at else None
                    })
                
                return {
                    "success": True,
                    "records": records,
                    "total": len(records)
                }
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados do CAR: {e}")
            return {"success": False, "message": f"Erro ao buscar dados: {str(e)}"}

# Instância global do gerenciador de banco de dados
db_manager = DatabaseManager() 
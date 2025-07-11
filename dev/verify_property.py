#!/usr/bin/env python3
# dev/verify_property.py
"""
Script para testar e comparar os arquivos ZIP com verificações rigorosas:
- Arquivo do estado completo (ex: data/MA_AREA_PROPERTY.zip)
- Arquivo da propriedade específica (ex: data/property_MA-2114007-FFFE73B6633D4199ACB914F4DFCCEEE4.zip)

USO:
    python3 test_files.py --state data/MA_AREA_PROPERTY.zip --property data/property_MA-2114007-FFFE73B6633D4199ACB914F4DFCCEEE4.zip

VERIFICAÇÕES:
1. Arquivo do Estado: Todos os registros são do Maranhão, todos os atributos obrigatórios presentes
2. Arquivo da Propriedade: Contém exatamente 1 registro com todos os atributos corretos
3. Comparação: Todos os atributos da propriedade batem entre os dois arquivos
"""

import zipfile
import geopandas as gpd
import tempfile
import os
import sys
import argparse
from typing import Dict, Any, Optional

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Verificação rigorosa de arquivos CAR - compara arquivo do estado com arquivo da propriedade",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLOS:
  python3 test_files.py --state data/MA_AREA_PROPERTY.zip --property data/property_MA-2114007-FFFE73B6633D4199ACB914F4DFCCEEE4.zip
  
  python3 test_files.py -s data/SP_AREA_PROPERTY.zip -p data/property_SP-1234567-ABCDEF.zip
  
  python3 test_files.py  # Usa valores padrão
        """
    )
    
    parser.add_argument(
        '--state', '-s',
        type=str,
        default='data/MA_AREA_PROPERTY.zip',
        help='Caminho para o arquivo ZIP do estado (padrão: data/MA_AREA_PROPERTY.zip)'
    )
    
    parser.add_argument(
        '--property', '-p',
        type=str,
        default='data/property_MA-2114007-FFFE73B6633D4199ACB914F4DFCCEEE4.zip',
        help='Caminho para o arquivo ZIP da propriedade (padrão: data/property_MA-2114007-FFFE73B6633D4199ACB914F4DFCCEEE4.zip)'
    )
    
    parser.add_argument(
        '--car', '-c',
        type=str,
        help='CAR específico para buscar (extraído automaticamente do nome do arquivo da propriedade se não fornecido)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Modo verboso - exibe informações detalhadas'
    )
    
    return parser.parse_args()

def extract_car_from_filename(filename: str) -> str:
    """Extrai o CAR do nome do arquivo da propriedade"""
    # Remove extensão e caminho
    basename = os.path.basename(filename)
    name_without_ext = os.path.splitext(basename)[0]
    
    # Remove prefixo 'property_' se existir
    if name_without_ext.startswith('property_'):
        car = name_without_ext[9:]  # Remove 'property_'
        return car
    
    return name_without_ext

def print_header(title: str):
    """Imprime um cabeçalho formatado"""
    print(f"\n{'='*80}")
    print(f"🔍 {title}")
    print(f"{'='*80}")

def print_section(title: str):
    """Imprime uma seção formatada"""
    print(f"\n{'─'*60}")
    print(f"📋 {title}")
    print(f"{'─'*60}")

def analyze_zip_file(zip_path: str, description: str) -> Optional[gpd.GeoDataFrame]:
    """Analisa um arquivo ZIP contendo shapefiles com verificações rigorosas"""
    print_header(f"ANÁLISE: {description}")
    print(f"📁 Arquivo: {zip_path}")
    print(f"📏 Tamanho: {os.path.getsize(zip_path):,} bytes")
    
    # Verificar se o arquivo existe
    if not os.path.exists(zip_path):
        print(f"❌ ERRO: Arquivo não encontrado: {zip_path}")
        return None
    
    # Listar conteúdo do ZIP
    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            print(f"\n📦 Conteúdo do ZIP ({len(zipf.infolist())} arquivos):")
            total_size = 0
            for info in zipf.infolist():
                print(f"  - {info.filename} ({info.file_size:,} bytes)")
                total_size += info.file_size
            print(f"  Total: {total_size:,} bytes")
    except zipfile.BadZipFile:
        print(f"❌ ERRO: Arquivo ZIP inválido: {zip_path}")
        return None
    
    # Extrair e analisar o shapefile
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(tmpdir)
            
            # Encontrar arquivo .shp
            shp_files = [f for f in os.listdir(tmpdir) if f.endswith('.shp')]
            if not shp_files:
                print("❌ ERRO: Nenhum arquivo .shp encontrado no ZIP")
                return None
            
            shp_path = os.path.join(tmpdir, shp_files[0])
            print(f"\n🗺️  Shapefile: {shp_files[0]}")
            
            # Ler com geopandas
            gdf = gpd.read_file(shp_path)
            print(f"📊 Número de registros: {len(gdf):,}")
            print(f"📋 Colunas ({len(gdf.columns)}): {list(gdf.columns)}")
            
            if len(gdf) > 0:
                print_section("ESTATÍSTICAS BÁSICAS")
                print(f"  CRS: {gdf.crs}")
                print(f"  Bounds: {gdf.total_bounds}")
                
                # Verificações específicas baseadas no tipo de arquivo
                if "AREA_PROPERTY" in zip_path or len(gdf) > 1000:  # Arquivo do estado
                    return validate_state_file(gdf, zip_path)
                else:
                    return validate_property_file(gdf, zip_path)
            else:
                print("❌ ERRO: Shapefile vazio!")
                return None
                
    except Exception as e:
        print(f"❌ ERRO ao processar shapefile: {str(e)}")
        return None

def validate_state_file(gdf: gpd.GeoDataFrame, zip_path: str, car_to_find: Optional[str] = None) -> gpd.GeoDataFrame:
    """Valida o arquivo do estado com verificações rigorosas"""
    print_section("VALIDAÇÃO DO ARQUIVO DO ESTADO")
    
    # Verificar se todos os registros são do Maranhão
    if 'cod_estado' in gdf.columns:
        ma_records = gdf[gdf['cod_estado'] == 'MA']
        total_records = len(gdf)
        ma_count = len(ma_records)
        
        print(f"  📍 Registros do Maranhão: {ma_count:,} / {total_records:,}")
        if ma_count == total_records:
            print("  ✅ Todos os registros são do Maranhão")
        else:
            print(f"  ⚠️  ATENÇÃO: {total_records - ma_count:,} registros não são do Maranhão!")
            
            # Mostrar estados únicos encontrados
            unique_states = gdf['cod_estado'].unique()
            print(f"  📊 Estados encontrados: {list(unique_states)}")
    else:
        print("  ⚠️  Campo 'cod_estado' não encontrado - não é possível validar estado")
    
    # Verificar campos obrigatórios
    required_fields = ['cod_imovel', 'municipio', 'num_area', 'geometry']
    missing_fields = [field for field in required_fields if field not in gdf.columns]
    
    if missing_fields:
        print(f"  ❌ Campos obrigatórios ausentes: {missing_fields}")
    else:
        print("  ✅ Todos os campos obrigatórios estão presentes")
    
    # Procurar o CAR específico se fornecido
    if car_to_find:
        car_fields = ["cod_imovel", "CAR", "COD_IMOVEL", "car", "codigo_car"]
        
        found_record = None
        for field in car_fields:
            if field in gdf.columns:
                found = gdf[gdf[field].astype(str).str.upper() == car_to_find.upper()]
                if not found.empty:
                    found_record = found.iloc[0]
                    print(f"\n  ✅ CAR {car_to_find} ENCONTRADO no arquivo do estado!")
                    print(f"     Campo usado: {field}")
                    print(f"     Posição: {found.index[0]}")
                    break
        else:
            print(f"\n  ❌ CAR {car_to_find} NÃO ENCONTRADO no arquivo do estado")
    
    return gdf

def validate_property_file(gdf: gpd.GeoDataFrame, zip_path: str) -> gpd.GeoDataFrame:
    """Valida o arquivo da propriedade com verificações rigorosas"""
    print_section("VALIDAÇÃO DO ARQUIVO DA PROPRIEDADE")
    
    # Verificar se contém exatamente 1 registro
    if len(gdf) == 1:
        print("  ✅ Arquivo contém exatamente 1 registro")
    else:
        print(f"  ❌ ERRO: Arquivo contém {len(gdf)} registros (esperado: 1)")
        return gdf
    
    # Verificar campos obrigatórios
    required_fields = ['cod_imovel', 'municipio', 'num_area', 'geometry']
    missing_fields = [field for field in required_fields if field not in gdf.columns]
    
    if missing_fields:
        print(f"  ❌ Campos obrigatórios ausentes: {missing_fields}")
    else:
        print("  ✅ Todos os campos obrigatórios estão presentes")
    
    # Verificar se é do Maranhão
    if 'cod_estado' in gdf.columns:
        if gdf.iloc[0]['cod_estado'] == 'MA':
            print("  ✅ Propriedade é do Maranhão")
        else:
            print(f"  ❌ ERRO: Propriedade não é do Maranhão (estado: {gdf.iloc[0]['cod_estado']})")
    
    return gdf

def display_property_details(gdf: gpd.GeoDataFrame, source: str):
    """Exibe todos os detalhes da propriedade"""
    print_section(f"DETALHES DA PROPRIEDADE ({source})")
    
    if len(gdf) == 0:
        print("  ❌ Nenhum registro encontrado")
        return
    
    record = gdf.iloc[0]
    
    # Exibir todos os campos
    for col in gdf.columns:
        value = record[col]
        if col == 'geometry':
            print(f"  {col}: {type(value).__name__} (área: {value.area:.6f} graus²)")
        else:
            print(f"  {col}: {value}")
    
    # Informações adicionais da geometria
    if 'geometry' in gdf.columns:
        geom = record['geometry']
        print(f"\n  🗺️  GEOMETRIA:")
        print(f"    Tipo: {type(geom).__name__}")
        print(f"    Área: {geom.area:.6f} graus²")
        print(f"    Bounds: {geom.bounds}")
        print(f"    Centroid: ({geom.centroid.x:.6f}, {geom.centroid.y:.6f})")

def compare_property_records(state_gdf: gpd.GeoDataFrame, property_gdf: gpd.GeoDataFrame, car_to_find: str):
    """Compara detalhadamente os registros da propriedade entre os dois arquivos"""
    print_header("COMPARAÇÃO DETALHADA DA PROPRIEDADE")
    
    # Encontrar o registro no arquivo do estado
    car_fields = ["cod_imovel", "CAR", "COD_IMOVEL", "car", "codigo_car"]
    
    state_record = None
    for field in car_fields:
        if field in state_gdf.columns:
            found = state_gdf[state_gdf[field].astype(str).str.upper() == car_to_find.upper()]
            if not found.empty:
                state_record = found.iloc[0]
                break
    
    if state_record is None:
        print("❌ ERRO: Não foi possível encontrar o registro no arquivo do estado")
        return
    
    if len(property_gdf) == 0:
        print("❌ ERRO: Arquivo da propriedade está vazio")
        return
    
    property_record = property_gdf.iloc[0]
    
    print_section("COMPARAÇÃO CAMPO A CAMPO")
    
    # Comparar todos os campos
    all_fields = set(state_gdf.columns) | set(property_gdf.columns)
    differences = []
    matches = []
    
    for field in sorted(all_fields):
        if field in state_gdf.columns and field in property_gdf.columns:
            state_value = state_record[field]
            property_value = property_record[field]
            
            if field == 'geometry':
                # Comparar geometrias
                if state_value.equals(property_value):
                    matches.append(f"  ✅ {field}: Geometrias idênticas")
                else:
                    differences.append(f"  ❌ {field}: Geometrias diferentes")
                    differences.append(f"     Estado: {type(state_value).__name__} (área: {state_value.area:.6f})")
                    differences.append(f"     Propriedade: {type(property_value).__name__} (área: {property_value.area:.6f})")
            else:
                # Comparar valores normais
                if state_value == property_value:
                    matches.append(f"  ✅ {field}: {state_value}")
                else:
                    differences.append(f"  ❌ {field}:")
                    differences.append(f"     Estado: {state_value}")
                    differences.append(f"     Propriedade: {property_value}")
        elif field in state_gdf.columns:
            differences.append(f"  ⚠️  {field}: Presente apenas no arquivo do estado")
        else:
            differences.append(f"  ⚠️  {field}: Presente apenas no arquivo da propriedade")
    
    # Exibir resultados
    print("📊 CAMPOS IDÊNTICOS:")
    for match in matches:
        print(match)
    
    if differences:
        print("\n📊 DIFERENÇAS ENCONTRADAS:")
        for diff in differences:
            print(diff)
    else:
        print("\n🎉 TODOS OS CAMPOS SÃO IDÊNTICOS!")
    
    # Resumo da comparação
    print_section("RESUMO DA COMPARAÇÃO")
    total_fields = len(all_fields)
    matching_fields = len([m for m in matches if m.startswith("  ✅")])
    
    print(f"  📊 Total de campos: {total_fields}")
    print(f"  ✅ Campos idênticos: {matching_fields}")
    print(f"  ❌ Diferenças: {len(differences)}")
    print(f"  📈 Taxa de correspondência: {(matching_fields/total_fields)*100:.1f}%")

def main():
    """Função principal"""
    # Parse arguments
    args = parse_arguments()
    
    # Extrair CAR do nome do arquivo se não fornecido
    car_to_find = args.car
    if not car_to_find:
        car_to_find = extract_car_from_filename(args.property)
    
    print_header("VERIFICAÇÃO RIGOROSA DE ARQUIVOS CAR")
    print(f"🔍 CAR sendo verificado: {car_to_find}")
    print(f"📁 Arquivo do Estado: {args.state}")
    print(f"📁 Arquivo da Propriedade: {args.property}")
    
    # Analisar arquivo do estado
    state_gdf = analyze_zip_file(args.state, "Arquivo do Estado")
    
    # Analisar arquivo da propriedade
    property_gdf = analyze_zip_file(args.property, "Arquivo da Propriedade Específica")
    
    # Exibir detalhes da propriedade em ambos os arquivos
    if state_gdf is not None:
        display_property_details(state_gdf, "Arquivo do Estado")
    
    if property_gdf is not None:
        display_property_details(property_gdf, "Arquivo da Propriedade")
    
    # Comparação detalhada
    if state_gdf is not None and property_gdf is not None:
        compare_property_records(state_gdf, property_gdf, car_to_find)
        
        # Estatísticas finais
        print_header("ESTATÍSTICAS FINAIS")
        print(f"📊 Arquivo do Estado:")
        print(f"   - Registros: {len(state_gdf):,}")
        print(f"   - Tamanho: {os.path.getsize(args.state):,} bytes")
        
        print(f"\n📊 Arquivo da Propriedade:")
        print(f"   - Registros: {len(property_gdf):,}")
        print(f"   - Tamanho: {os.path.getsize(args.property):,} bytes")
        
        compression_ratio = (1 - len(property_gdf) / len(state_gdf)) * 100
        size_ratio = (1 - os.path.getsize(args.property) / os.path.getsize(args.state)) * 100
        
        print(f"\n📉 Redução de registros: {compression_ratio:.2f}%")
        print(f"📉 Redução de tamanho: {size_ratio:.2f}%")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Análise interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        sys.exit(1) 
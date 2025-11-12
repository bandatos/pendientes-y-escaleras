from typing import TYPE_CHECKING

from rest_framework.decorators import action
from django.http import FileResponse
from yeeko_xlsx_export.generic import export_xlsx


if TYPE_CHECKING:
    from rest_framework.viewsets import ModelViewSet
else:
    class ModelViewSet:
        pass


class ExportXlsMixin(ModelViewSet):
    action_add_file_param: str = ""
    # xls_name: str = "Export"
    xls_attrs: list = []
    add_locations = False
    location_attrs: list = [
        {
            "name": "ID de ubicación principal",
            "width": 5,
            "field": "location_id",
        },
        {
            "name": "ID de Entidad",
            "width": 4,
            "field": "state__inegi_code",
            "subquery": "locations"
        },
        {
            "name": "Entidad",
            "width": 25,
            "field": "state__short_name",
            "subquery": "locations"
        },
        {
            "name": "ID de Municipio",
            "width": 4,
            "field": "municipality__inegi_code",
            "subquery": "locations"
        },
        {
            "name": "Municipio",
            "width": 25,
            "field": "municipality__name",
            "subquery": "locations"
        },
        {
            "name": "ID de Localidad",
            "width": 4,
            "field": "locality__inegi_code",
            "subquery": "locations"
        },
        {
            "name": "Localidad",
            "width": 25,
            "field": "locality__name",
            "subquery": "locations"
        },
        {
            "name": "Latitud",
            "width": 12,
            "field": "latitude",
            "subquery": "locations"
        },
        {
            "name": "Longitud",
            "width": 12,
            "field": "longitude",
            "subquery": "locations"
        }
    ]
    max_decimal: int = 2

    def get_query_for_export_xls(self):
        return self.filter_queryset(self.get_queryset())

    @action(detail=False, methods=['get'])
    def export_xls(self, request):
        serializer = self.get_serializer(
            self.get_query_for_export_xls(), many=True)

        data = serializer.data

        name = getattr(self, 'xls_name', None)
        if not name:
            name = self.queryset.model._meta.verbose_name_plural
        attrs = getattr(self, 'xls_attrs', [])
        if self.add_locations:
            attrs = attrs + getattr(self, 'location_attrs', [])
        columns_width = [row.get('width', 20) for row in attrs]
        heades = [row.get('name', '') for row in attrs]
        # columns_width_pixel
        max_decimal = getattr(self, 'max_decimal', 2)

        table_data = [heades]
        for row in data:
            row_data = []
            # table_data.append([row.get(attr['field'], '') for attr in attrs])
            for attr in attrs:
                field = attr.get('field', '')
                if field:
                    value = row
                    if attr.get('subquery'):
                        value = row.get(field, '')
                    else:
                        for key in field.split('__'):
                            try:
                                value = value.get(key, '')
                            except AttributeError as e:
                                # print(f"Error accessing {key} in {value}\n{row}")
                                value = ''
                    row_data.append(value)
                else:
                    row_data.append('')
            table_data.append(row_data)

        # print(table_data)

        response = export_xlsx(
            in_memory=True, data=[{
                "name": name,
                "table_data": table_data,
                "columns_width": columns_width,
                # "columns_width_pixel": columns_width,
                "max_decimal": max_decimal
            }])

        response.seek(0)
        return FileResponse(response, as_attachment=True, filename=f"{name}.xlsx")

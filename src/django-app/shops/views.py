from django.shortcuts import render
from django.db import transaction
from django.core.exceptions import ValidationError
from django.apps import apps

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_access_policy import AccessViewSetMixin
from rest_framework.decorators import action

from accounts.serializers import EmployeeDataSerializer

from datetime import datetime, timedelta
import json
import traceback
import logging

from .serializers import (
    ShopSerializer,
    ShopWriteSerializer,
    ShopAvailabilitySerializer,
    AddressSerializer,
    InvitationSerializer,
    ServicePartSerializer,
    ServiceSerializer,
    ServiceUpdateSerializer,
    AppointmentSerializer,
    AppointmentCreateSerializer,
    AppointmentUpdateSerializer,
    AppointmentSlotSerializer,
    AppointmentSlotListSerializer,
    AppointmentSlotUpdateSerializer,
    WorkOrderSerializer,
    WorkOrderCreateSerializer,
    WorkOrderUpdateSerializer,
)
from .models import (
    Shop,
    ShopAvailability,
    ShopHours,
    Address,
    Invitation,
    Service,
    ServicePart,
    AppointmentSlot,
    Appointment,
    WorkOrder,
)
from .policies import (
    ShopAccessPolicy,
    AddressAccessPolicy,
    ServiceAccessPolicy,
    AppointmentAccessPolicy,
    AppointmentSlotAccessPolicy,
    WorkOrderAccessPolicy,
)

from vehicles.models import Part


class ShopViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    access_policy = ShopAccessPolicy
    queryset = Shop.objects.all().order_by("name")

    def get_queryset(self):
        return self.access_policy.scope_queryset(self.request, self.queryset)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ShopWriteSerializer
        return ShopSerializer

    def partial_update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                shop = self.get_object()
                shop_services = request.data.pop("shop_services", None)
                if shop_services is not None:
                    Service.objects.filter(
                        id__in=shop_services, shop__id=shop.id
                    ).update(active=True)
                    Service.objects.filter(shop__id=shop.id).exclude(
                        id__in=shop_services
                    ).update(active=False)

                address = request.data.pop("address", None)
                if address is not None:
                    address_object = Address.objects.get(id=address.get("id"))
                    address_serializer = AddressSerializer(
                        address_object, data=address, partial=True
                    )
                    if address_serializer.is_valid(raise_exception=True):
                        address_serializer.save()

                shop_hours = request.data.pop("shophours_set", None)
                if shop_hours is not None:
                    for shop_hour in shop_hours:
                        try:
                            obj, created = ShopHours.objects.update_or_create(
                                shop=shop,
                                day=shop_hour.get("day", None),
                                defaults={
                                    "from_time": shop_hour.get("from_time", None),
                                    "to_time": shop_hour.get("to_time", None),
                                },
                            )
                        except Exception as e:
                            logging.error(traceback.format_exc())
                    shop_hours_days = [i.get("day") for i in shop_hours]
                    ShopHours.objects.filter(shop=shop).exclude(
                        day__in=shop_hours_days
                    ).delete()

                shop_serializer = ShopWriteSerializer(
                    shop, data=request.data, partial=True
                )
                if shop_serializer.is_valid(raise_exception=True):
                    shop_serializer.save()
                return Response(shop_serializer.data)
        except Exception as err:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["get"])
    def employees(self, request, *args, **kwargs):
        shop = self.get_object()
        serializer = EmployeeDataSerializer(shop.get_employees(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def me(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            if request.user.type == "shop_owner":
                shop = queryset.filter(shop_owner=request.user).first()
            elif request.user.type == "employee":
                EmployeeData = apps.get_model("accounts", "EmployeeData")
                employee = EmployeeData.objects.filter(user=request.user).first()
                shop = employee.shop
            else:
                raise ValidationError(
                    "Only shop owners and employees can access this endpoint"
                )
            serializer = ShopSerializer(shop, context={"request": request})
            return Response(serializer.data)
        except Exception as e:
            logging.error(traceback.format_exc())
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )


class AddressViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    access_policy = AddressAccessPolicy
    queryset = Address.objects.all().order_by("street")
    serializer_class = AddressSerializer


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer


class ServiceViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    access_policy = ServiceAccessPolicy
    queryset = Service.objects.all()

    def get_queryset(self):
        return self.access_policy.scope_queryset(self.request, self.queryset)

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return ServiceUpdateSerializer
        return ServiceSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                parts = data.pop("parts", None)
                service_serializer = ServiceSerializer(data=data)
                if service_serializer.is_valid(raise_exception=True):
                    service = service_serializer.save()
                    if parts is not None:
                        service_parts_to_create = Part.objects.filter(
                            id__in=parts
                        )
                        for part in service_parts_to_create:
                            service_part_serializer = ServicePartSerializer(service=service, part=part.pk, price=part.price, quantity=1)
                            if service_part_serializer.is_valid(raise_exception=True):
                                service_part_serializer.save()
                return Response(service_serializer.data)
        except Exception as err:
            return Response(
                {"status": False, "error_description": 'Failed to create service.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                updated_service = self.get_object()
                data = request.data
                parts = data.pop("parts", None)
                service_serializer = ServiceSerializer(updated_service, data=data, partial=True)
                if service_serializer.is_valid(raise_exception=True):
                    service_serializer.save()
                    if parts is not None:
                        service_parts_fetched = Part.objects.filter(
                            id__in=parts
                        )
                        
                        ServicePart.objects.filter(
                            service=updated_service.pk
                        ).exclude(
                            id__in=[part.id for part in service_parts_fetched]
                        ).delete()

                        for part in service_parts_fetched:
                            try:
                                obj, created = ServicePart.objects.update_or_create(
                                    service=updated_service,
                                    part=part.pk,
                                    defaults={
                                        "price": part.price,
                                        "quantity": 1
                                    },
                                )
                            except Exception as err:
                                logging.error(traceback.format_exc())
                return Response(service_serializer.data)
        except Exception as err:
            return Response(
                {"status": False, "error_description": 'Failed to update service.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ServicePartViewSet(viewsets.ModelViewSet):
    queryset = ServicePart.objects.all()
    serializer_class = ServicePartSerializer


class AppointmentViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    access_policy = AppointmentAccessPolicy
    queryset = Appointment.objects.all()

    def get_queryset(self):
        queryset = self.access_policy.scope_queryset(self.request, self.queryset)
        queryset = self._filter_by_shop(queryset)
        queryset = self._filter_by_status(queryset)
        return queryset

    def get_serializer_class(self):
        if self.action in ["create"]:
            return AppointmentCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return AppointmentUpdateSerializer
        return AppointmentSerializer

    def _filter_by_shop(self, queryset):
        shop_id = self.request.GET.get("shop")
        if shop_id is not None:
            return queryset.filter(shop=shop_id)
        else:
            return queryset

    def _filter_by_status(self, queryset):
        status = self.request.GET.get("status")
        if status is not None:
            return queryset.filter(status=status)
        else:
            return queryset

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                appointment_slots = data.pop("appointment_slots")
                appointment_serializer = self.get_serializer_class()(data=data)
                if appointment_serializer.is_valid(raise_exception=True):
                    appointment = appointment_serializer.save()
                    slots = AppointmentSlot.objects.filter(
                        pk__in=appointment_slots
                    ).order_by("start_time")

                    if slots.count() != len(appointment_slots):
                        raise ValidationError("Incorrect slots were requested.")

                    duration_sum = timedelta(minutes=0)
                    through_appointments = []
                    for slot in slots:
                        # ensure slot is available
                        if not slot.is_available:
                            raise ValidationError(f"{slot} is unavailable.")

                        if slot.shop != appointment.shop:
                            raise ValidationError(
                                f"Invalid slot for the respective shop."
                            )

                        duration_sum += slot.duration
                        through_appointments.append(
                            AppointmentSlot.appointments.through(
                                appointment_id=appointment.id,
                                appointmentslot_id=slot.id,
                            )
                        )

                    # ensure slots are sorted and not missing a slot
                    if (
                        (
                            duration_sum
                            != slots.last().end_time - slots.first().start_time
                        )
                        or (appointment.duration > duration_sum)
                        or (
                            duration_sum - appointment.duration >= timedelta(minutes=15)
                        )
                    ):
                        raise ValidationError(
                            f"Invalid duration or slots selected for the appointment."
                        )

                    AppointmentSlot.appointments.through.objects.bulk_create(
                        through_appointments
                    )
                return Response(
                    {
                        "status": True,
                        "results": "Appointment Created",
                        "data": AppointmentSerializer(appointment).data,
                    },
                    status=status.HTTP_201_CREATED,
                )
        except ValidationError as err:
            return Response(
                {"status": False, "error_description": err.message},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AppointmentSlotViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    access_policy = AppointmentSlotAccessPolicy
    queryset = AppointmentSlot.objects.all()

    def get_serializer_class(self):
        if self.action in ["list"]:
            return AppointmentSlotListSerializer
        elif self.action in ["update", "partial_update"]:
            return AppointmentSlotUpdateSerializer
        return AppointmentSlotSerializer

    def get_queryset(self):
        queryset = self.access_policy.scope_queryset(self.request, self.queryset)
        queryset = self._filter_by_shop(queryset)
        queryset = self._filter_by_start_date(queryset)
        queryset = self._filter_by_end_date(queryset)
        queryset = self._filter_by_available_appointments(queryset)
        return queryset

    def _filter_by_shop(self, queryset):
        shop_id = self.request.GET.get("shop")
        if shop_id is not None:
            return queryset.filter(shop=shop_id)
        else:
            return queryset

    def _filter_by_start_date(self, queryset):
        try:
            start_date = datetime.combine(
                self.request.GET.get("start_date"), datetime.min.time()
            )
            return queryset.filter(start_time__gte=start_date)
        except:
            return queryset

    def _filter_by_end_date(self, queryset):
        try:
            end_date = datetime.combine(
                self.request.GET.get("end_date"), datetime.max.time()
            )
            return queryset.filter(end_time__lte=end_date)
        except:
            return queryset

    def _filter_by_available_appointments(self, queryset):
        try:
            available_only = json.loads(self.request.GET.get("available_only"))
            if type(available_only) is bool and available_only:
                return (slot for slot in queryset if slot.is_available)
            else:
                return queryset
        except:
            return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        duration_minutes = int(self.request.GET.get("minutes", 0))
        if duration_minutes == 0:
            serializer = AppointmentSlotSerializer(queryset, many=True)
            return Response(serializer.data)

        duration = timedelta(minutes=duration_minutes)
        query_list = []
        for slot in list(queryset):
            q_set = slot.get_current_plus_duration(duration)
            if q_set is not None and q_set.count() != 0:
                serializer = self.get_serializer_class()(q_set, many=True)
                query_list.append(serializer.data)
        return Response({"slots": query_list})


class WorkOrderViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    access_policy = WorkOrderAccessPolicy
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer

    def get_queryset(self):
        return self.access_policy.scope_queryset(self.request, self.queryset)

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return WorkOrderUpdateSerializer
        elif self.action in ["create"]:
            return WorkOrderCreateSerializer
        return WorkOrderSerializer


class ShopAvailabilityViewSet(viewsets.ModelViewSet):
    # access_policy = ShopAvailabilityAccessPolicy
    queryset = ShopAvailability.objects.all()
    serializer_class = ShopAvailabilitySerializer

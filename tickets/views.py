from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView


class WelcomeView(View):
    @staticmethod
    def get(self, request, *args, **kwargs):
        html = '<h2>Welcome to the Hypercar Service!</h2>'
        return HttpResponse(html)


class MenuView(View):
    template_name = 'tickets/menu.html'
    menu = {"Change oil": "/change_oil",
            "Inflate tires": "/inflate_tires",
            "Get diagnostic test": "/diagnostic"}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={'menu': self.menu})


class TicketNumberView(TemplateView):
    template_name = 'tickets/get_number.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        ticket_type = kwargs['ticket_type']
        ticket = Ticket(ticket_type)
        number, time = TicketQueue().enqueue_ticket(ticket)
        data['ticket_number'] = number
        data['minutes_to_wait'] = time
        ticket.set_ticket_number(number)
        return data


class TicketQueue(object):
    _instance = None
    change_oil = "change_oil"
    inflate_tires = "inflate_tires"
    diagnostic = "diagnostic"

    def __new__(self):
        if not self._instance:
            self._instance = super(TicketQueue, self).__new__(self)
            self.queue = {self.change_oil: [], self.inflate_tires: [], self.diagnostic: []}
            self.next_ticket_number = 1
            self.tmp = None
        return self._instance

    def enqueue_ticket(self, ticket):
        number = self.next_ticket_number
        self.next_ticket_number += 1
        time = self.calculate_minutes_to_wait(ticket)
        self.queue[ticket.get_ticket_type()].append(ticket)
        return number, time

    def calculate_time_wait_for_change_oil(self):
        return Ticket(self.change_oil).get_operation_time() * len(self.queue.get(self.change_oil))

    def calculate_time_wait_for_inflate_tires(self):
        return Ticket(self.inflate_tires).get_operation_time() * len(self.queue.get(self.inflate_tires))

    def calculate_time_wait_for_diagnostic(self):
        return Ticket(self.diagnostic).get_operation_time() * len(self.queue.get(self.diagnostic))

    def calculate_minutes_to_wait(self, ticket):
        time_to_wait = {self.change_oil: self.calculate_time_wait_for_change_oil(),
                        self.inflate_tires: self.calculate_time_wait_for_inflate_tires() + \
                                            self.calculate_time_wait_for_change_oil(),
                        self.diagnostic: self.calculate_time_wait_for_inflate_tires() + \
                                         self.calculate_time_wait_for_diagnostic() + \
                                         self.calculate_time_wait_for_change_oil()}
        return time_to_wait.get(ticket.get_ticket_type())

    def get_queue_status(self):
        return [len(self.queue.get(i)) for i in self.queue]

    def get_next_ticket_from_queue(self):
        if self.queue.get(self.change_oil):
            return self.queue.get(self.change_oil)[0]
        else:
            if self.queue.get(self.inflate_tires):
                return self.queue.get(self.inflate_tires)[0]
            else:
                if self.queue.get(self.diagnostic):
                    return self.queue.get(self.diagnostic)[0]
        return None

    def remove_ticket_from_queue(self):
        if not self.tmp:
            return None
        self.queue.get(self.tmp.get_ticket_type()).pop(0)

    def set_tmp_queue(self):
        self.tmp = self.get_next_ticket_from_queue()

    def get_next_ticket(self):
        return self.tmp

    def get_ticket_to_processing(self):
        self.set_tmp_queue()
        self.remove_ticket_from_queue()
        return self.tmp


class Ticket:
    change_oil = "change_oil"
    inflate_tires = "inflate_tires"
    diagnostic = "diagnostic"

    operation_times = {change_oil: 2, inflate_tires: 5, diagnostic: 30}

    def __init__(self, ticket_type):
        self.ticket_type = ticket_type
        self.ticket_number = 0

    def get_operation_time(self):
        return self.operation_times.get(self.ticket_type)

    def set_ticket_number(self, number):
        self.ticket_number = number

    def get_ticket_type(self):
        return self.ticket_type

    def get_ticket_number(self):
        return self.ticket_number


class ProcessingView(View):
    template_name = 'tickets/operator_menu.html'

    def get(self, request, *args, **kwargs):
        change_oil, inflate_tires, get_diagnostic = TicketQueue().get_queue_status()
        data = {'change_oil_number': change_oil,
                'inflate_tires_number': inflate_tires,
                'diagnostic_test_number': get_diagnostic}
        return render(request, template_name=self.template_name, context=data)

    def post(self, request, *args, **kwargs):
        next_ticket = None
        ticket = TicketQueue().get_ticket_to_processing()
        if ticket:
            next_ticket = ticket.get_ticket_number()
        request.POST.get("next_ticket")
        return redirect("/next/"+str(next_ticket), *args, **kwargs)


class NextView(View):
    template_name = "tickets/next.html"

    def get(self, request, *args, **kwargs):
        ticket = TicketQueue().get_next_ticket()
        if "next_ticket" in kwargs:
            next_ticket = kwargs["next_ticket"]
        else:
            next_ticket = None
            if ticket:
                next_ticket = ticket.get_ticket_number()
        data = {"next_ticket": next_ticket}
        return render(request, self.template_name, context=data)

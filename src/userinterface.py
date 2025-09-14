from nicegui import ui, binding
import asyncio
import threading
from functools import partial
import math

from src import Index, Search, Document, ElasticsearchClient
from src.utils import QueryParser


class Userinterface:
    """
    This class handles the userinterface for the IR anthology boolean search demo.
    """
    use_embeddings = binding.BindableProperty()

    def __init__(self):
        self.queue_lock = threading.Lock()
        self.es_client = ElasticsearchClient()
        self._index = Index(self.es_client)
        self._search = Search(self.es_client)
        self.query_parser = QueryParser(use_self_implemented=False)
        self.use_embeddings = False
        self.only_search_title_abstract = False
        self.search_bar_input = ""
        self.last_response = None
        self.page = 1
        self.max_num_results = 10
    
    def update_search_bar_input(self, new_search_bar_input):
        """
        Updates the search_bar_input variable.

        Args:
            new_search_bar_input: The search bar with the new input.
        """
        self.search_bar_input = new_search_bar_input.value
    
    def build_userinterface(self):
        """
        Builds the initial userinterface.
        """
        with ui.column().classes('mx-auto items-center w-full') as self.root:
            # Title
            with ui.row().classes('p-0 gap-3'):
                ui.label('IR').style('font-size: 300%; font-weight: bold; color: #9f371d;')
                self.title_label = ui.label(' Anthology - Boolean Search Demo').style('font-size: 300%; font-weight: bold;')
            
            # Search field
            with ui.row().classes('mx-auto items-center w-full justify-center p-0 gap-3'):
                self.search_field = ui.input(placeholder='Search the IR-Anthology...', on_change=self.update_search_bar_input) \
                                        .props('rounded outlined dense autogrow autofocus') \
                                        .classes('w-2/3') \
                                        .on('keypress.enter', lambda e: None if e.args['shiftKey'] else self.on_enter_search(), args=['shiftKey']) \
                                        .on("keypress", js_handler="""
                                            (e) => { 
                                                if (!e.shiftKey && e.key === "Enter") { 
                                                    e.preventDefault()
                                                }
                                            }
                                        """)
                with ui.link(target='https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax', new_tab=True):
                    ui.button(icon='o_info').props('flat fab color=black').tooltip('View the query syntax documentation.')
            with self.search_field.add_slot("append"):
                with ui.button(icon='more_vert').props('flat fab color=black'):
                    with ui.menu():
                        ui.checkbox("Only search in title and abstract") \
                            .classes('ml-2 mr-4').props('color=black') \
                            .bind_value(self, "only_search_title_abstract")
                ui.button(icon='search', on_click=self.on_enter_search).props('flat fab color=black')
            ui.separator()

            # Results container
            self.results = ui.column().classes('w-2/3')
    
    async def on_enter_search(self):
        """
        This functions handles what happens when entering the search.
        """
        self.results.clear()
        self.page = 1
        await self.search()
    
    async def search(self):
        """
        Searches the IR anthology index with the current search_bar_input and refreshes the UI with the results.
        """
        self.search_field.disable()
        with self.root:
            spinner = ui.spinner(size='128px', color='#9f371d')
        
        loop = asyncio.get_event_loop()
        input_string = self.search_bar_input
        # Build the Elasticsearch query
        query = self.query_parser.build_query(input_string, only_search_title_abstract=self.only_search_title_abstract)
        if self.use_embeddings:
            with self.queue_lock:
                if not self._index.model:
                    await loop.run_in_executor(None, self._index.init_embedding_model)
                embedding = await loop.run_in_executor(None, partial(self._index.get_embedding, input_string))
            query = self.query_parser.build_dense_vector_query(query, embedding)
        
        # Perform the search
        from_ = (self.page-1)*self.max_num_results
        size = self.max_num_results
        try:
            response = await loop.run_in_executor(None, partial(self._search.search, query['query'], from_, size))
        except Exception as e:
            print(e)
            spinner.delete()
            self.show_error()
            self.search_field.enable()
            return

        # Update the UI with the documents in the response
        self.last_response = response['hits']['hits']
        self.current_total = response['hits']['total']
        await loop.run_in_executor(None, partial(self.update_results))
        spinner.delete()
        self.search_field.enable()
    
    def update_results(self):
        """
        Update the results UI with the last_response.
        """
        if len(self.last_response) == 0:
            with self.results:
                ui.label(f'No results with this query.')
            return

        first_index = (self.page-1)*self.max_num_results
        last_index = min(first_index+self.max_num_results, self.current_total)
        num_results = last_index - first_index
        num_pages = math.ceil(self.current_total / self.max_num_results)
        with self.results:
            with ui.row().classes('w-full'):
                ui.label(f'Showing results {first_index+1}-{last_index}.')
                ui.space()
                ui.label(f'Total results: {self.current_total}')
            with ui.column():
                for idx in range(num_results):
                    self.display_search_result(Document(self.last_response[idx]))
            with ui.row().classes('mx-auto items-center'):
                self.pagination = ui.pagination(1, num_pages, value=self.page, direction_links=True, on_change=self.navigate_page).props(':max-pages=10 boundary-numbers color=black')
    
    def display_search_result(self, result):
        """
        Display a single search result.

        Args:
            result: The document object containing the result.
        """
        with ui.column().classes('p-0 gap-0'):
            ui.link(result.title, target=result.url, new_tab=True).style('font-size: 120%; font-weight: bold; color: #9f371d;').classes('no-underline')
            ui.label(f'Year: {result.year}')
            ui.label(f'Venue: {result.venue}')
            ui.label(f'Authors: {"; ".join(result.author)}')
            ui.html(result.get_highlight('full_text'))
    
    async def navigate_page(self):
        """
        Navigate to the clicked page in the pagination and updates the results UI.
        """
        self.page = self.pagination.value
        self.results.clear()
        ui.navigate.to(self.title_label)
        await self.search()

    def show_error(self):
        """
        Show an error message on the results UI.
        """
        with self.results:
            ui.label('Something went wrong. Please make sure to use the search operators correctly!').style('color: red;')


@ui.page('/demo')
def start_demo():
    """
    This function renders the demo application.
    """
    webUI = Userinterface()
    webUI.build_userinterface()

@ui.page('/')
def start_app():
    """
    This is the auto-index page.
    This function should be called to start rendering the app.
    """
    ui.navigate.to('/demo')

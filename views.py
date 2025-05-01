from django.urls import reverse_lazy
from django.views import generic
from .models import Category
from .forms import CategoryForm

#Listar Categorias
class CategoryListView(generic.ListView):
      model = Category
      template_name = 'categories/category_list.html'

#Crear categoria
class CategoryCreateView(generic.CreateView):
      model = Category
      form_class = CategoryForm
      template_name = 'categories/category_form.html'
      success_url = reverse_lazy('category_list')

# Modificar categoría
class CategoryUpdateView(generic.UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_url = reverse_lazy('category_list')

# Borrar categoría
class CategoryDeleteView(generic.DeleteView):
    model = Category
    template_name = 'categories/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')


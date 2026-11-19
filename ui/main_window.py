import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from ui.components import BG, PANEL, CARD, TEXT, MUTED, ACCENT, configure_style

class ShopFlowWindow:
    def __init__(self, root, catalog, cart, checkout, customers, promotions, users, reports):
        self.root, self.catalog, self.cart, self.checkout = root, catalog, cart, checkout
        self.customers, self.promotions, self.users, self.reports = customers, promotions, users, reports
        self.current_user = None
        self.root.title("ShopFlow | Commerce Management")
        self.root.geometry("1280x820"); self.root.minsize(1050, 680)
        configure_style(root)
        self._login()

    @staticmethod
    def money(value): return "$" + f"{value:,.0f}".replace(",", ".")

    def _login(self):
        for child in self.root.winfo_children(): child.destroy()
        frame = tk.Frame(self.root, bg=BG); frame.pack(expand=True)
        tk.Label(frame, text="SHOPFLOW", bg=BG, fg=ACCENT, font=("Segoe UI", 30, "bold")).pack(pady=(0,4))
        tk.Label(frame, text="COMMERCE MANAGEMENT SYSTEM", bg=BG, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(pady=(0,24))
        tk.Label(frame, text="Usuario", bg=BG, fg=TEXT).pack(anchor="w")
        username = tk.StringVar(value="admin"); user_entry = ttk.Entry(frame, textvariable=username, width=34); user_entry.pack(pady=(5,14))
        tk.Label(frame, text="Contraseña", bg=BG, fg=TEXT).pack(anchor="w")
        password = tk.StringVar(); pass_entry = ttk.Entry(frame, textvariable=password, show="*", width=34); pass_entry.pack(pady=(5,18))
        def login():
            user = self.users.authenticate(username.get(), password.get())
            if not user: messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos."); return
            self.current_user = user; self._build_shell()
        ttk.Button(frame, text="Ingresar", style="Accent.TButton", command=login).pack(fill="x")
        tk.Label(frame, text="Primer acceso: admin / ShopFlow2026*", bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(pady=15)
        pass_entry.bind("<Return>", lambda _e: login())

    def _build_shell(self):
        for child in self.root.winfo_children(): child.destroy()
        shell = tk.Frame(self.root, bg=BG); shell.pack(fill="both", expand=True)
        self.sidebar = tk.Frame(shell, bg=PANEL, width=225); self.sidebar.pack(side="left", fill="y"); self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="SHOPFLOW", bg=PANEL, fg=ACCENT, font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=22, pady=(25,2))
        tk.Label(self.sidebar, text="COMMERCE MANAGEMENT", bg=PANEL, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=23, pady=(0,20))
        self.content = tk.Frame(shell, bg=BG); self.content.pack(side="left", fill="both", expand=True, padx=26, pady=22)
        nav = [("▦  Dashboard","dashboard",self.show_dashboard),("▤  Productos","products",self.show_products),
               ("⇄  Inventario","inventory",self.show_inventory),("🛒  Carrito","cart",self.show_cart),
               ("▣  Pedidos y pagos","orders",self.show_orders),("♙  Clientes","customers",self.show_customers),
               ("％  Promociones","promotions",self.show_promotions)]
        for label, permission, callback in nav:
            if self.users.allowed(self.current_user, permission):
                ttk.Button(self.sidebar, text=label, style="Nav.TButton", command=callback).pack(fill="x", padx=12, pady=3)
        ttk.Button(self.sidebar, text="⇩  Exportar pedidos CSV", style="Nav.TButton", command=self.export_orders).pack(fill="x", padx=12, pady=(18,3))
        ttk.Button(self.sidebar, text="⇩  Exportar productos CSV", style="Nav.TButton", command=self.export_products).pack(fill="x", padx=12, pady=3)
        if self.users.allowed(self.current_user, "all"):
            ttk.Button(self.sidebar, text="⚙  Usuarios", style="Nav.TButton", command=self.show_users).pack(fill="x", padx=12, pady=3)
        tk.Label(self.sidebar, text=f"{self.current_user['username']} · {self.current_user['role']}", bg=PANEL, fg=MUTED, font=("Segoe UI", 8)).pack(side="bottom", anchor="w", padx=18, pady=8)
        ttk.Button(self.sidebar, text="Cerrar sesión", style="Nav.TButton", command=self._login).pack(side="bottom", fill="x", padx=12, pady=(0,12))
        self.show_dashboard()

    def _clear(self):
        for child in self.content.winfo_children(): child.destroy()
    def _header(self, title, subtitle):
        ttk.Label(self.content, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.content, text=subtitle, style="Sub.TLabel").pack(anchor="w", pady=(4,18))
    def _stat(self, parent, label, value):
        card = ttk.Frame(parent, style="Card.TFrame", padding=15); card.pack(side="left", fill="both", expand=True, padx=(0,10))
        ttk.Label(card, text=label, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(card, text=str(value), style="CardValue.TLabel").pack(anchor="w", pady=(7,0))
    def _table(self, parent, columns, headings, height=12):
        wrap = ttk.Frame(parent); wrap.pack(fill="both", expand=True)
        tree = ttk.Treeview(wrap, columns=columns, show="headings", height=height)
        for col, heading, width in headings:
            tree.heading(col, text=heading); tree.column(col, width=width, anchor="w")
        scroll = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview); tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
        return tree
    def _selected(self, table):
        sel = table.selection()
        return table.item(sel[0], "values") if sel else None

    def show_dashboard(self):
        self._clear(); self._header("Dashboard", "Indicadores de operación, inventario y ventas.")
        products = self.catalog.all(); stats_data = self.checkout.stats()
        cards = ttk.Frame(self.content); cards.pack(fill="x", pady=(0,18))
        self._stat(cards,"PRODUCTOS",len(products)); self._stat(cards,"STOCK DISPONIBLE",sum(p.stock for p in products))
        self._stat(cards,"PEDIDOS PENDIENTES",stats_data["pending"]); self._stat(cards,"VENTAS PAGADAS",self.money(stats_data["revenue"]))
        cards2 = ttk.Frame(self.content); cards2.pack(fill="x", pady=(0,22))
        self._stat(cards2,"PEDIDOS REGISTRADOS",stats_data["orders"]); self._stat(cards2,"CANCELADOS",stats_data["cancelled"])
        self._stat(cards2,"TICKET PROMEDIO",self.money(stats_data["average"]))
        ttk.Label(self.content,text="Últimos pedidos",font=("Segoe UI",13,"bold")).pack(anchor="w",pady=(0,8))
        table=self._table(self.content,("id","customer","total","status","date"),[("id","PEDIDO",100),("customer","CLIENTE",170),("total","TOTAL",120),("status","ESTADO",120),("date","FECHA",200)],8)
        for o in self.checkout.history()[:12]: table.insert("","end",values=(o.id,o.customer,self.money(o.total),o.status,o.created_at.replace("T"," ")))

    def show_products(self):
        self._clear(); self._header("Catálogo de productos","Gestiona el catálogo. La búsqueda exacta utiliza el árbol AVL.")
        bar=ttk.Frame(self.content); bar.pack(fill="x",pady=(0,12))
        term=tk.StringVar(); entry=ttk.Entry(bar,textvariable=term,width=32); entry.pack(side="left",padx=(0,7))
        table=self._table(self.content,("id","name","category","price","stock"),[("id","ID",75),("name","PRODUCTO",240),("category","CATEGORÍA",150),("price","PRECIO",130),("stock","STOCK",80)],13)
        def populate(items=None):
            table.delete(*table.get_children())
            for p in items if items is not None else self.catalog.all():
                table.insert("","end",values=(p.id,p.name,p.category,self.money(p.price),p.stock))
        def search(): populate(self.catalog.search(term.get()) if term.get().strip() else None)
        ttk.Button(bar,text="Buscar AVL",command=search).pack(side="left")
        ttk.Button(bar,text="Todos",command=populate).pack(side="left",padx=5)
        ttk.Button(bar,text="+ Nuevo",style="Accent.TButton",command=lambda:self.product_dialog()).pack(side="right")
        ttk.Button(bar,text="Eliminar",command=lambda:self.delete_product(table)).pack(side="right",padx=5)
        ttk.Button(bar,text="Editar",command=lambda:self.edit_product(table)).pack(side="right",padx=5)
        populate(); entry.bind("<Return>",lambda _e:search())

    def product_dialog(self, product=None):
        dialog=tk.Toplevel(self.root); dialog.title("Editar producto" if product else "Nuevo producto"); dialog.configure(bg=BG); dialog.transient(self.root); dialog.grab_set(); dialog.resizable(False,False)
        fields={}
        values={"name":product.name if product else "", "category":product.category if product else "General",
                "price":str(product.price) if product else "", "stock":str(product.stock) if product else "0"}
        for i,(key,label) in enumerate([("name","Nombre"),("category","Categoría"),("price","Precio COP"),("stock","Stock")]):
            tk.Label(dialog,text=label,bg=BG,fg=TEXT).grid(row=i,column=0,sticky="w",padx=15,pady=8)
            fields[key]=tk.StringVar(value=values[key]); ttk.Entry(dialog,textvariable=fields[key],width=30).grid(row=i,column=1,padx=15,pady=8)
        def save():
            try:
                if product:
                    self.catalog.update(product.id,fields["name"].get(),fields["category"].get(),float(fields["price"].get()))
                    new_stock=int(fields["stock"].get())
                    if new_stock != product.stock: self.catalog.adjust_stock(product.id,new_stock-product.stock,"Edición desde catálogo")
                else: self.catalog.add(fields["name"].get(),fields["category"].get(),float(fields["price"].get()),int(fields["stock"].get()))
                dialog.destroy(); self.show_products()
            except (ValueError,TypeError) as exc: messagebox.showerror("Datos inválidos",str(exc),parent=dialog)
        ttk.Button(dialog,text="Guardar cambios",style="Accent.TButton",command=save).grid(row=4,column=0,columnspan=2,pady=14)
    def edit_product(self,table):
        row=self._selected(table)
        if not row: messagebox.showwarning("Selecciona","Selecciona un producto."); return
        self.product_dialog(self.catalog.get(row[0]))
    def delete_product(self,table):
        row=self._selected(table)
        if not row: messagebox.showwarning("Selecciona","Selecciona un producto."); return
        pending_ids={i.product_id for o in self.checkout.pending() for i in o.items}
        try:
            if messagebox.askyesno("Confirmar",f"¿Eliminar {row[1]}?"):
                self.catalog.delete(row[0],set(self.cart.items),pending_ids); self.show_products()
        except ValueError as exc: messagebox.showerror("No se puede eliminar",str(exc))

    def show_cart(self):
        self._clear(); self._header("Carrito","Historial LIFO: deshacer y rehacer operaciones.")
        bar=ttk.Frame(self.content); bar.pack(fill="x",pady=(0,12))
        ttk.Button(bar,text="+ Agregar producto",style="Accent.TButton",command=self.add_to_cart).pack(side="left")
        ttk.Button(bar,text="Cambiar cantidad",command=lambda:self.change_cart_qty(table)).pack(side="left",padx=6)
        ttk.Button(bar,text="Quitar",command=lambda:self.remove_cart_item(table)).pack(side="left")
        ttk.Button(bar,text="Deshacer",command=lambda:self.cart_action("undo")).pack(side="right",padx=5)
        ttk.Button(bar,text="Rehacer",command=lambda:self.cart_action("redo")).pack(side="right")
        table=self._table(self.content,("id","name","qty","unit","subtotal"),[("id","ID",80),("name","PRODUCTO",250),("qty","CANTIDAD",90),("unit","UNITARIO",130),("subtotal","SUBTOTAL",130)],12)
        lines,total=self.cart.lines()
        for p,q,s in lines: table.insert("","end",values=(p.id,p.name,q,self.money(p.price),self.money(s)))
        footer=ttk.Frame(self.content); footer.pack(fill="x",pady=15)
        ttk.Label(footer,text=f"TOTAL: {self.money(total)}",font=("Segoe UI",17,"bold")).pack(side="left")
        ttk.Button(footer,text="Confirmar pedido →",style="Accent.TButton",command=self.submit_order).pack(side="right")
    def add_to_cart(self):
        choices="\n".join(f"{p.id} | {p.name} | stock {p.stock}" for p in self.catalog.all())
        pid=simpledialog.askstring("Agregar","ID del producto:\n\n"+choices,parent=self.root)
        if not pid:return
        qty=simpledialog.askinteger("Cantidad","Unidades:",minvalue=1,parent=self.root)
        if qty is None:return
        try:self.cart.add(pid.strip().upper(),qty); self.show_cart()
        except ValueError as exc:messagebox.showerror("Error",str(exc))
    def change_cart_qty(self,table):
        row=self._selected(table)
        if not row:messagebox.showwarning("Selecciona","Selecciona un artículo.");return
        qty=simpledialog.askinteger("Cantidad","Nueva cantidad (0 elimina):",minvalue=0,parent=self.root)
        if qty is None:return
        try:self.cart.set_quantity(row[0],qty);self.show_cart()
        except ValueError as exc:messagebox.showerror("Error",str(exc))
    def remove_cart_item(self,table):
        row=self._selected(table)
        if not row:messagebox.showwarning("Selecciona","Selecciona un artículo.");return
        try:self.cart.remove(row[0]);self.show_cart()
        except ValueError as exc:messagebox.showerror("Error",str(exc))
    def cart_action(self,action):
        changed=self.cart.undo() if action=="undo" else self.cart.redo()
        if not changed:messagebox.showinfo("Historial","No hay acciones disponibles.")
        self.show_cart()
    def submit_order(self):
        name=simpledialog.askstring("Cliente","Nombre del cliente:",parent=self.root)
        if name is None:return
        phone=simpledialog.askstring("Cliente","Teléfono (opcional):",parent=self.root) or ""
        email=simpledialog.askstring("Cliente","Correo (opcional):",parent=self.root) or ""
        code=simpledialog.askstring("Promoción","Código de descuento (deja vacío si no aplica):",parent=self.root) or ""
        try:
            order=self.checkout.submit(name,phone,email,code)
            messagebox.showinfo("Pedido registrado",f"Pedido {order.id} en cola FIFO.\nTotal: {self.money(order.total)}")
            self.show_orders()
        except ValueError as exc:messagebox.showerror("No se pudo registrar",str(exc))

    def show_orders(self):
        self._clear();self._header("Pedidos y pagos","Consulta pedidos, abre su detalle, cancela pendientes y procesa la cola FIFO.")
        bar=ttk.Frame(self.content);bar.pack(fill="x",pady=(0,10))
        term=tk.StringVar();entry=ttk.Entry(bar,textvariable=term,width=30);entry.pack(side="left")
        table=self._table(self.content,("id","customer","total","status","date"),[("id","PEDIDO",100),("customer","CLIENTE",170),("total","TOTAL",120),("status","ESTADO",130),("date","FECHA",200)],11)
        def populate():
            table.delete(*table.get_children())
            for o in self.checkout.find(term.get()):
                table.insert("","end",values=(o.id,o.customer,self.money(o.total),o.status,o.created_at.replace("T"," ")))
        ttk.Button(bar,text="Buscar",command=populate).pack(side="left",padx=6)
        ttk.Button(bar,text="Ver todos",command=lambda:(term.set(""),populate())).pack(side="left")
        actions=ttk.Frame(self.content);actions.pack(fill="x",pady=10)
        ttk.Button(actions,text="Ver detalle",command=lambda:self.order_detail(table)).pack(side="left")
        ttk.Button(actions,text="Cancelar pendiente",command=lambda:self.cancel_order(table)).pack(side="left",padx=6)
        ttk.Button(actions,text="Procesar siguiente FIFO",style="Accent.TButton",command=self.process_payment).pack(side="right")
        populate();entry.bind("<Return>",lambda _e:populate())
    def order_detail(self,table):
        row=self._selected(table)
        if not row:messagebox.showwarning("Selecciona","Selecciona un pedido.");return
        o=self.checkout.get(row[0])
        dialog=tk.Toplevel(self.root);dialog.title(f"Pedido {o.id}");dialog.configure(bg=BG);dialog.geometry("620x480")
        tk.Label(dialog,text=f"PEDIDO {o.id}",bg=BG,fg=ACCENT,font=("Segoe UI",18,"bold")).pack(anchor="w",padx=20,pady=15)
        tk.Label(dialog,text=f"Cliente: {o.customer}     Estado: {o.status}\nFecha: {o.created_at}\nCódigo: {o.discount_code or '—'}",bg=BG,fg=TEXT,justify="left").pack(anchor="w",padx=20)
        table2=self._table(dialog,("name","qty","unit","subtotal"),[("name","PRODUCTO",220),("qty","CANT.",70),("unit","PRECIO",110),("subtotal","SUBTOTAL",120)],8)
        subtotal=0
        for i in o.items:
            line=i.unit_price*i.quantity;subtotal+=line
            table2.insert("","end",values=(i.name,i.quantity,self.money(i.unit_price),self.money(line)))
        tk.Label(dialog,text=f"Subtotal: {self.money(subtotal)}    Descuento: {self.money(o.discount_amount)}    TOTAL: {self.money(o.total)}",bg=BG,fg=TEXT,font=("Segoe UI",12,"bold")).pack(anchor="e",padx=20,pady=10)
        ttk.Button(dialog,text="Generar comprobante PDF",style="Accent.TButton",command=lambda:self.receipt(o)).pack(anchor="e",padx=20,pady=8)
    def cancel_order(self,table):
        row=self._selected(table)
        if not row:messagebox.showwarning("Selecciona","Selecciona un pedido.");return
        if not messagebox.askyesno("Cancelar pedido",f"¿Cancelar {row[0]} y devolver las unidades al inventario?"):return
        try:self.checkout.cancel(row[0]);self.show_orders()
        except ValueError as exc:messagebox.showerror("No se puede cancelar",str(exc))
    def process_payment(self):
        o=self.checkout.process_next()
        if o is None:messagebox.showinfo("Cola vacía","No hay pagos pendientes.")
        else:messagebox.showinfo("Pago simulado",f"Pedido {o.id} marcado como PAGADO.\nTotal: {self.money(o.total)}")
        self.show_orders()

    def show_inventory(self):
        self._clear();self._header("Movimientos de inventario","Trazabilidad de entradas, reservas, reintegros y ajustes.")
        bar=ttk.Frame(self.content);bar.pack(fill="x",pady=(0,10))
        ttk.Button(bar,text="Registrar ajuste",style="Accent.TButton",command=self.inventory_adjust).pack(side="left")
        table=self._table(self.content,("id","product","type","qty","reason","date"),[("id","MOV.",80),("product","PRODUCTO",180),("type","TIPO",120),("qty","CANT.",70),("reason","MOTIVO",220),("date","FECHA",190)],14)
        for m in self.catalog.movements():table.insert("","end",values=(m["id"],m["product_name"],m["type"],m["quantity"],m["reason"],m["date"].replace("T"," ")))
    def inventory_adjust(self):
        products="\n".join(f"{p.id} | {p.name} | stock {p.stock}" for p in self.catalog.all())
        pid=simpledialog.askstring("Ajuste","ID del producto:\n"+products,parent=self.root)
        if not pid:return
        delta=simpledialog.askinteger("Ajuste","Cantidad a sumar (positivo) o restar (negativo):",parent=self.root)
        if delta is None or delta==0:return
        reason=simpledialog.askstring("Motivo","Motivo del ajuste:",parent=self.root) or "Ajuste manual"
        try:self.catalog.adjust_stock(pid.strip().upper(),delta,reason);self.show_inventory()
        except ValueError as exc:messagebox.showerror("Error",str(exc))

    def show_customers(self):
        self._clear();self._header("Clientes","Directorio de clientes registrados al realizar pedidos.")
        table=self._table(self.content,("id","name","phone","email","created"),[("id","ID",90),("name","CLIENTE",200),("phone","TELÉFONO",140),("email","CORREO",220),("created","REGISTRO",190)],14)
        for c in self.customers.all():table.insert("","end",values=(c["id"],c["name"],c.get("phone",""),c.get("email",""),c.get("created_at","")))
        ttk.Button(self.content,text="Editar cliente seleccionado",command=lambda:self.edit_customer(table)).pack(anchor="e",pady=10)

    def edit_customer(self, table):
        row=self._selected(table)
        if not row:messagebox.showwarning("Selecciona","Selecciona un cliente.");return
        customer=next((c for c in self.customers.all() if c["id"]==row[0]),None)
        if not customer:return
        dialog=tk.Toplevel(self.root);dialog.title("Editar cliente");dialog.configure(bg=BG);dialog.transient(self.root);dialog.grab_set();dialog.resizable(False,False)
        fields={}
        for i,(key,label) in enumerate([("name","Nombre"),("phone","Teléfono"),("email","Correo")]):
            tk.Label(dialog,text=label,bg=BG,fg=TEXT).grid(row=i,column=0,sticky="w",padx=15,pady=8)
            fields[key]=tk.StringVar(value=customer.get(key,""))
            ttk.Entry(dialog,textvariable=fields[key],width=34).grid(row=i,column=1,padx=15,pady=8)
        def save():
            try:
                self.customers.update(customer["id"],fields["name"].get(),fields["phone"].get(),fields["email"].get())
                dialog.destroy();self.show_customers()
            except ValueError as exc:messagebox.showerror("Error",str(exc),parent=dialog)
        ttk.Button(dialog,text="Guardar",style="Accent.TButton",command=save).grid(row=3,column=0,columnspan=2,pady=12)
    def show_promotions(self):
        self._clear();self._header("Descuentos y promociones","Crea códigos porcentuales y activa o desactiva promociones.")
        bar=ttk.Frame(self.content);bar.pack(fill="x",pady=(0,12))
        ttk.Button(bar,text="+ Nueva promoción",style="Accent.TButton",command=self.create_promotion).pack(side="left")
        table=self._table(self.content,("code","percent","active","date"),[("code","CÓDIGO",160),("percent","DESCUENTO",130),("active","ESTADO",110),("date","CREADA",150)],12)
        for p in self.promotions.all():table.insert("","end",values=(p["code"],f"{p['percent']}%", "ACTIVA" if p["active"] else "INACTIVA",p["created_at"]))
        ttk.Button(self.content,text="Activar / desactivar seleccionada",command=lambda:self.toggle_promotion(table)).pack(anchor="e",pady=10)
    def create_promotion(self):
        code=simpledialog.askstring("Promoción","Código:",parent=self.root)
        if not code:return
        percent=simpledialog.askfloat("Promoción","Porcentaje de descuento (1 a 90):",minvalue=1,maxvalue=90,parent=self.root)
        if percent is None:return
        try:self.promotions.create(code,percent);self.show_promotions()
        except ValueError as exc:messagebox.showerror("Error",str(exc))
    def toggle_promotion(self,table):
        row=self._selected(table)
        if not row:messagebox.showwarning("Selecciona","Selecciona una promoción.");return
        self.promotions.toggle(row[0]);self.show_promotions()

    def show_users(self):
        self._clear();self._header("Usuarios y permisos","Gestión de cuentas locales con contraseñas derivadas mediante PBKDF2.")
        bar=ttk.Frame(self.content);bar.pack(fill="x",pady=(0,12))
        ttk.Button(bar,text="+ Crear usuario",style="Accent.TButton",command=self.create_user).pack(side="left")
        table=self._table(self.content,("username","role","active"),[("username","USUARIO",200),("role","ROL",160),("active","ACTIVO",100)],10)
        for u in self.users.all():table.insert("","end",values=(u["username"],u["role"],"Sí" if u["active"] else "No"))
        tk.Label(self.content,text="ADMIN: acceso total · INVENTARIO: catálogo e inventario · VENTAS: carrito, pedidos, clientes y promociones.",bg=BG,fg=MUTED,wraplength=850,justify="left").pack(anchor="w",pady=14)
    def create_user(self):
        username=simpledialog.askstring("Usuario","Nombre de usuario:",parent=self.root)
        if not username:return
        password=simpledialog.askstring("Usuario","Contraseña (mínimo 8 caracteres):",show="*",parent=self.root)
        if password is None:return
        role=simpledialog.askstring("Rol","Escribe ADMIN, INVENTARIO o VENTAS:",parent=self.root)
        if not role:return
        try:self.users.create(username,password,role.strip().upper());self.show_users()
        except ValueError as exc:messagebox.showerror("Error",str(exc))

    def receipt(self,order):
        path=filedialog.asksaveasfilename(defaultextension=".pdf",initialfile=f"ShopFlow_{order.id}.pdf",filetypes=[("PDF","*.pdf")])
        if not path:return
        try:self.reports.receipt_pdf(order,path);messagebox.showinfo("Comprobante",f"PDF guardado en:\n{path}")
        except (RuntimeError,OSError) as exc:messagebox.showerror("No se pudo generar",str(exc))
    def export_orders(self):
        path=filedialog.asksaveasfilename(defaultextension=".csv",initialfile="pedidos_shopflow.csv",filetypes=[("CSV","*.csv")])
        if not path:return
        try:self.reports.export_orders_csv(path);messagebox.showinfo("Exportación",f"Archivo guardado:\n{path}")
        except OSError as exc:messagebox.showerror("Error",str(exc))
    def export_products(self):
        path=filedialog.asksaveasfilename(defaultextension=".csv",initialfile="productos_shopflow.csv",filetypes=[("CSV","*.csv")])
        if not path:return
        try:self.reports.export_products_csv(path);messagebox.showinfo("Exportación",f"Archivo guardado:\n{path}")
        except OSError as exc:messagebox.showerror("Error",str(exc))

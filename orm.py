from datetime import datetime
from sqlalchemy import(Table, Column, Integer, Numeric, String, DateTime, ForeignKey, Boolean, create_engine, desc)
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base=declarative_base()

class Cookie(Base):#Hereda de la clase Base
    __tablename__="cookies"

    cookie_id=Column(Integer(), primary_key=True)#Definimos un atributo y configuramos como clave principal
    cookie_name=Column(String(50), index=True)
    cookie_recipe_url=Column(String(255))
    cookie_sku=Column(String(55))
    quantity=Column(Integer())
    unit_cost=Column(String(10))#Numeric(12,2)

    def __repr__(self):
        return "Cookie(cookie_name='{self.cookie_name}',"\
            "cookie_recipe_url='{self.cookie_recipe_url}',"\
            "cookie_sku='{self.cookie_sku}',"\
            "quantity={self.quantity},"\
            "unit_cost={self.unit_cost})".format(self=self)

class User(Base):
    __tablename__="users"

    user_id = Column(Integer(), primary_key=True)
    username = Column(String(15), nullable=False, unique=True)#Requiriendo que la columna sea obligatoria y unica
    email_address = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    password = Column(String(25), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)#
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return "User(username='{self.username}',"\
            "email_address='{self.email_address}',"\
            "phone='{self.phone}',"\
            "password='{self.password}".format(self=self)

#Llaves y restricciones
class Order(Base):
    __tablename__="orders"

    order_id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey("users.user_id"))
    shipped = Column(Boolean(), default=False)#No sale en el diagrama de entidad relacion
    user = relationship("User", backref=backref("orders"))#Order_by=order_id)) Relacion 1:M
    
    def __repr__(self):
        return "Order(user_id={self.user_id}, " \
            "shipped={self.shipped})".format(self=self)

class LineItem(Base):
    __tablename__="line_items"
    line_item_id=Column(Integer(), primary_key=True)
    order_id=Column(Integer(), ForeignKey("orders.order_id"))
    cookie_id=Column(Integer(), ForeignKey("cookies.cookie_id"))
    quantity=Column(Integer())
    extended_cost=Column(String(10))#Aqui va Numeric(12, 2)
    order=relationship("Order", backref=backref("line_items", order_by=line_item_id))#Relacion M:1
    cookie=relationship("Cookie", uselist=False, order_by=cookie_id)#Establece relacion uno a uno

    def __repr__(self):
        return "LineItems(order_id={self.order_id},"\
            "cookie_id={self.cookie_id},"\
            "quantity={self.quantity}",\
            "extended_cost={self.extended_cost}".format(self=self)

#Creacion del esquema
engine=create_engine("sqlite:///C:\\Users\\Baez\\Desktop\\datos\\virtual\\ormdata.db") 
Base.metadata.drop_all(engine)#Borra las tablas o limpiarlas
Base.metadata.create_all(engine)

#La sesion es la manera qye sqlalchemy interactura con la base de datos
Session=sessionmaker(bind=engine)
session=Session()

#INSERTANDO DATOS
"""#Un solo objeto
cc_cookie=Cookie(cookie_name='chocolate chip', cookie_recipe_url='chocolatechip.com', cookie_sku='CC01', quantity=12,unit_cost=0.50)
session.add(cc_cookie)#Agregamos la instancia a la sesion
session.commit()
print(cc_cookie.cookie_id)#Imprimimos el id de la cookie"""
#Multiples objetos
cc_cookie = Cookie(cookie_name='chocolate chip', cookie_recipe_url='chocolatechip.com', cookie_sku='CC01', quantity=12,unit_cost=5.1)
dcc=Cookie(cookie_name='dark chocolate chip', cookie_recipe_url='darkchocolatechip.com', cookie_sku='CC02', quantity=1, unit_cost=7.25)
mol=Cookie(cookie_name="molasses",cookie_recipe_url="molasses.com",cookie_sku="MOL01",quantity=1,unit_cost=8.125)
c1=Cookie(cookie_name="peanut butter", cookie_recipe_url="peanut.com", cookie_sku="PB01", quantity=24, unit_cost=0.20)
c2=Cookie(cookie_name="oatmel raisin", cookie_recipe_url="oatmel.com", cookie_sku="EWW01", quantity=100, unit_cost=0.80)

#1er metodo, cuando se hara algo extra con la adicion de los datos
session.bulk_save_objects([cc_cookie, dcc, mol, c1, c2])
session.commit()

#Consultar datos
"""cookies=session.query(Cookie).all()
print(cookies)
print("\n")
for cookie in session.query(Cookie):
    print(cookie)"""

#Controlando las columnas en la consulta
"""cookies=session.query(Cookie.cookie_name, Cookie.quantity).all()
for cookie in cookies:
    print(cookie)
#Envia el primero que encuentre
cookies=session.query(Cookie.cookie_name, Cookie.quantity).first()
for cookie in cookies:
    print(cookie)"""

#Ordenar los datos consultados
#ordenar por cantodad ascendente
"""cookies=session.query(Cookie).order_by(Cookie.quantity)
for cookie in cookies:
    print("{:3} - {}".format(cookie.quantity, cookie.cookie_name))
#prdenar por orden descendente
cookies=session.query(Cookie).order_by(desc(Cookie.quantity))
for cookie in cookies:
    print("{:3} - {}".format(cookie.quantity, cookie.cookie_name))"""

#Limitar los datos consultados
#Realizamos un inventario rapidamente mediante el uso de listas
"""cookies = session.query(Cookie).order_by(Cookie.quantity)[:3]
for cookie in cookies:
    print(cookie.cookie_name)
#Tambien se puede hacer mediante el metodo limit()
cookies = session.query(Cookie).order_by(Cookie.quantity).limit(3)
for cookie in cookies:
    print(cookie.cookie_name)"""

#Funciones y etiquetas SQL integradas
#Sumando las cookies
"""from sqlalchemy import func
inventario=session.query(func.sum(Cookie.quantity)).scalar()
print(inventario)
#Cuantos registros hay en el inventario
recuento = session.query(func.count(Cookie.cookie_name)).first()
print(recuento)"""

#Renombrando columna
from sqlalchemy import func
"""inventario=session.query(func.count(Cookie.cookie_name).label('cuenta_inventario')).first()
print(inventario.keys())
print(inventario.cuenta_inventario)"""

#Actualizando datos
#Primero metodo
"""print(cc_cookie.quantity)#Consultamos cantidad 
query=session.query(Cookie)
cc_cookie=query.filter(Cookie.cookie_name=="chocolate chip").first()
cc_cookie.quantity=cc_cookie.quantity + 200
session.commit()
print(cc_cookie.quantity)#Verificamos cantidad
#Segundo metodo
print(cc_cookie.quantity)
query=session.query(Cookie)
query=query.filter(Cookie.cookie_name=="chocolate chip")
query.update({Cookie.quantity: Cookie.quantity + 200})
cc_cookie=query.first()
print(cc_cookie.quantity)"""

#Borrando datos
#Primer metodo
"""query=session.query(Cookie)
query=query.filter(Cookie.cookie_name=="dark chocolate chip")
dcc_cookie=query.one()
print(dcc_cookie)#Consultamos
session.delete(dcc_cookie)
session.commit()
dcc_cookie=query.first()
print(dcc_cookie)#Verificamos"""

#Segundo metodo, no hace commit
query=session.query(Cookie)
query = query.filter(Cookie.cookie_name == "molasses")
#print(query)
query.delete()
mol_cookie = query.first()
print(mol_cookie)